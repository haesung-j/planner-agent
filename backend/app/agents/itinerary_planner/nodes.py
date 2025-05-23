from langchain_core.messages import AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.config import get_stream_writer

from app.config import config
from app.agents.itinerary_planner.chains import (
    create_itinerary_info_gather_chain,
    create_itinerary_planner_chain,
)
from app.agents.base import BaseNode


class ItineraryInformationGatherer(BaseNode):
    def __init__(self, name: str = "ItineraryInformationGatherer", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.ITINERARY_PLANNER_MODEL

    async def arun(self, state):
        writer = get_stream_writer()

        places = state.get("places", "")
        chain = create_itinerary_info_gather_chain(self.model_name, places)
        messages = state["messages"]
        response = []
        tool_calls = None

        first = True
        async for chunk in chain.astream({"messages": messages}):
            if chunk.tool_call_chunks:
                if first:
                    tool_calls = chunk
                    first = False
                else:
                    tool_calls += chunk
            elif chunk.content:
                response.append(chunk.content)
                writer(chunk.content)
            else:
                continue

        if response:
            response = AIMessage(content="".join(response), name="itinerary_planner")
            return {"messages": [response]}
        else:
            return {"messages": [tool_calls]}


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
        chain = create_itinerary_planner_chain(self.model_name)
        response = await chain.ainvoke(state["messages"])
        return {"messages": [response], "itinerary": response.content}
