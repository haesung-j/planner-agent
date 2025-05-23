from typing import cast
from langchain_core.messages import AIMessage

from app.agents.base import BaseNode
from app.agents.supervisor.chains import create_supervisor_chain
from app.config import config

# from langgraph.types import StreamWriter
from langgraph.config import get_stream_writer


class Supervisor(BaseNode):
    def __init__(self, name: str = "Supervisor", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.SUPERVISOR_MODEL

    async def arun(self, state):
        messages = state["messages"]
        chain = create_supervisor_chain(self.model_name)
        response = await chain.ainvoke(messages)

        if response.next == "itinerary_planner":
            return {
                "next": response.next,
                "reason": response.reason,
            }
        else:
            writer = get_stream_writer()
            writer(response.notification)
            return {
                "next": response.next,
                "reason": response.reason,
                "messages": AIMessage(content=response.notification, name="supervisor"),
            }
