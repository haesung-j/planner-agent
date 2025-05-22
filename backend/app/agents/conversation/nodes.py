from typing import cast
from langchain_core.messages import AIMessage

from app.config import config
from app.agents.conversation.chains import create_conversation_chain
from app.agents.base import BaseNode


class GeneralConversation(BaseNode):
    def __init__(self, name: str = "GeneralConversation", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.GENERAL_CONVERSATION_MODEL

    async def arun(self, state):
        chain = create_conversation_chain(self.model_name)

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
                    )
                ]
            }
        return {"messages": [response]}
