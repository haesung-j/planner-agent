from typing import cast
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from app.config import config
from app.agents.itinerary_planner.chains import create_itinerary_planner_chain
from app.agents.base import BaseNode
from app.agents.utils import places_to_readable_format


class ItineraryPlannerAgent(BaseNode):
    def __init__(self, name: str = "ItineraryPlannerAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.ITINERARY_PLANNER_MODEL

    async def arun(self, state):
        chain = create_itinerary_planner_chain(self.model_name)

        response = cast(
            AIMessage,
            await chain.ainvoke(state.messages),
        )
        response.name = "itinerary_planner"
        return {"messages": [response]}
