from typing import cast
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from app.agents.place_researcher.tools import (
    web_search,
    search_place,
    get_place_details,
)
from app.config import config
from app.agents.place_researcher.chains import (
    create_place_researcher_chain,
    create_place_researcher_response,
)
from app.agents.base import BaseNode
from app.agents.utils import places_to_readable_format


class PlaceResearcherAgent(BaseNode):
    def __init__(self, name: str = "PlaceResearcherAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.PLACE_RESEARCHER_MODEL

    async def arun(self, state):
        chain = create_place_researcher_chain(self.model_name)

        response = cast(
            AIMessage,
            await chain.ainvoke(state.messages),
        )

        # 마지막 단계인데도 모델이 도구를 사용하려는 경우
        if state.is_last_step and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="죄송합니다. 질문에 대한 답변을 찾을 수 없습니다.",
                        name="place_researcher",
                    )
                ]
            }

        response.name = "place_researcher"
        return {"messages": [response]}


class PlaceResearcherTools(ToolNode):
    def __init__(self, **kwargs):
        super().__init__(
            tools=[
                # web_search,
                search_place,
                get_place_details,
            ],
            name="place_researcher_tools",
            **kwargs,
        )


class PlaceResponse(BaseNode):
    def __init__(self, name: str = "PlaceResponse", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.PLACE_RESPONSE_MODEL

    async def arun(self, state):
        chain = create_place_researcher_response(self.model_name)

        response = cast(
            AIMessage,
            await chain.ainvoke([HumanMessage(content=state.messages[-2].content)]),
        )

        if hasattr(response, "place_info") and response.place_info is not None:
            response_formatted = places_to_readable_format(response.place_info)
            response_formatted = AIMessage(
                content=response_formatted, name="place_researcher"
            )
            return {
                "messages": [response_formatted],
                "places": response.place_info,
            }

        # response.place_info is None
        response_formatted = AIMessage(
            content="죄송합니다. 질문에 대한 답변을 찾을 수 없습니다.",
            name="place_researcher",
        )
        return {"messages": [response_formatted]}
