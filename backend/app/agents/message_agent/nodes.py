from typing import cast
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

from app.config import config
from app.agents.message_agent.chains import create_message_chain
from app.agents.base import BaseNode


class MessageAgent(BaseNode):
    def __init__(self, name: str = "MessageAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.GENERAL_CONVERSATION_MODEL

    async def arun(self, state):
        chain = create_message_chain(self.model_name)

        writer = get_stream_writer()

        first = True
        response = []
        async for chunk in chain.astream(state["messages"]):
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
            response = AIMessage(content="".join(response), name="message_agent")
            return {"messages": [response]}
        else:
            return {"messages": [tool_calls]}
