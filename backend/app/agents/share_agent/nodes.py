from typing import cast
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode

from app.agents.google_tools import gmail_tools
from app.config import config
from app.agents.share_agent.chains import create_share_chain
from app.agents.base import BaseNode


class ShareAgent(BaseNode):
    def __init__(self, name: str = "ShareAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.SHARE_AGENT_MODEL

    async def arun(self, state):
        chain = create_share_chain(self.model_name, state.get("itinerary", ""))

        response = cast(
            AIMessage,
            await chain.ainvoke(state.get("messages", [])),
        )
        response.name = "share_agent"
        # 마지막 단계인데도 모델이 도구를 사용하려는 경우
        if state.get("is_last_step", False) and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="죄송합니다. 질문에 대한 답변을 찾을 수 없습니다.",
                    )
                ]
            }
        return {"messages": [response]}


class ShareTools(ToolNode):
    def __init__(self, **kwargs):
        super().__init__(tools=gmail_tools, name="share_tools", **kwargs)
