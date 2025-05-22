from typing import cast
from langchain_core.messages import AIMessage

from app.agents.base import BaseNode
from app.agents.supervisor.chains import create_supervisor_chain
from app.config import config


# class Supervisor(BaseNode):
#     def __init__(self, name: str = "Supervisor", **kwargs):
#         super().__init__(name, **kwargs)
#         self.model_name = config.SUPERVISOR_MODEL

#     async def arun(self, state):
#         messages = state["messages"]
#         chain = create_supervisor_chain(self.model_name)
#         response = await chain.ainvoke(messages)
#         return {
#             "next": response.next,
#             "reason": response.reason,
#             "messages": AIMessage(content=response.answer),
#         }


class Supervisor(BaseNode):
    def __init__(self, name: str = "Supervisor", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.SUPERVISOR_MODEL

    async def arun(self, state):
        messages = state["messages"]
        chain = create_supervisor_chain(self.model_name)
        response = await chain.ainvoke(messages)
        return {
            "next": response.next,
            "reason": response.reason,
        }
