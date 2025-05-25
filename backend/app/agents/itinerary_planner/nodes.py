from typing import cast
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

# from langgraph.config import get_stream_writer

from app.config import config
from app.agents.itinerary_planner.chains import (
    create_itinerary_info_gather_chain,
    create_itinerary_planner_chain,
)
from app.agents.base import BaseNode
from app.agents.utils import format_places_to_string


class ItineraryInformationGatherer(BaseNode):
    def __init__(self, name: str = "ItineraryInformationGatherer", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.ITINERARY_PLANNER_MODEL

    async def arun(self, state):
        selected_places = state.get("selected_places", [])
        chain = create_itinerary_info_gather_chain(
            self.model_name, format_places_to_string(selected_places)
        )
        print("!" * 100)
        print(format_places_to_string(selected_places))
        messages = state["messages"]
        response = cast(
            AIMessage,
            await chain.ainvoke(messages),
        )
        response.name = "itinerary_planner"
        # 마지막 단계인데도 모델이 도구를 사용하려는 경우
        if state["is_last_step"] and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="죄송합니다. 질문에 대한 답변을 찾을 수 없습니다.",
                    )
                ]
            }
        return {"messages": [response]}


def add_tool_message(state):
    return {
        "messages": [
            ToolMessage(
                content="itinerary 생성 완료",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        ]
    }


class ItineraryPlannerAgent(BaseNode):
    def __init__(self, name: str = "ItineraryPlannerAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.ITINERARY_PLANNER_MODEL

    async def arun(self, state):
        selected_places = state.get("selected_places", [])
        chain = create_itinerary_planner_chain(
            self.model_name, format_places_to_string(selected_places)
        )
        messages = state["messages"]
        response = await chain.ainvoke(messages)
        return {"messages": [response], "itinerary": response.content}
