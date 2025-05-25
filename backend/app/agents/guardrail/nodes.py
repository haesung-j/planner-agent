from langchain_groq import ChatGroq
from typing import List, Literal
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import load_prompt
from langgraph.config import get_stream_writer
from langgraph.graph.message import RemoveMessage

from app.agents.base import BaseNode
from app.config import config
from app.agents.guardrail.state import GuardrailOutput


unsafe_content_categories = {
    "S1": "폭력 범죄 (살인, 테러, 폭행, 아동학대 등)",
    "S2": "비폭력 범죄 (사기, 절도, 해킹, 마약 등)",
    "S3": "성범죄 (성폭행, 성희롱, 성매매 등)",
    "S4": "아동 성 착취",
    "S5": "명예훼손 (허위사실 유포)",
    "S6": "전문 조언 (의료, 법률, 금융 등)",
    "S7": "개인정보 노출",
    "S8": "지적재산권 침해",
    "S9": "대량살상무기 (화학, 생물학, 핵무기 등)",
    "S10": "혐오 표현 (인종, 종교, 성별 차별 등)",
    "S11": "자살 및 자해",
    "S12": "성적 콘텐츠",
    "S13": "선거 관련 허위정보",
    "S14": "코드 악용 (해킹, 시스템 공격 등)",
}


class SafetyCheck(BaseNode):

    def __init__(self, name="Guardrail", role=Literal["human", "ai"], **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.GUARDRAIL_MODEL
        self.guardrail = ChatGroq(model=self.model_name)
        self.role = role

    async def arun(self, state):
        conversation_history = self._format_messages(state["messages"])
        system_prompt = load_prompt("app/prompts/guardrail.yaml")
        system_prompt = system_prompt.format(
            role=self.role, conversation_history=conversation_history
        )
        response = await self.guardrail.ainvoke(system_prompt)
        return {"safety_check": self._parse_response(response)}

    def _format_messages(self, messages: List[BaseMessage]):
        msg_str = []
        if self.role == "human":
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    msg_str.append(f"Human: {msg.content}\n")
        elif self.role == "ai":
            for msg in messages:
                if isinstance(msg, AIMessage):
                    msg_str.append(f"AI: {msg.content}")
        return "\n\n".join(msg_str)

    def _parse_response(self, response) -> GuardrailOutput:
        result = response.content.split()

        safety_check = result[0]
        unsafe_code = result[1] if len(result) > 1 else ""
        unsafe_reason = unsafe_content_categories.get(unsafe_code, "Unknown")
        return GuardrailOutput(
            safety_check=safety_check,
            unsafe_code=unsafe_code,
            unsafe_reason=unsafe_reason,
        )


class FormatSafetyMessage(BaseNode):
    def __init__(self, name="FormatSafetyMessage", **kwargs):
        super().__init__(name, **kwargs)

    async def arun(self, state):
        writer = get_stream_writer()
        content = f"이 대화는 안전하지 않아 종료됩니다. {state['safety_check'].unsafe_code}: {state['safety_check'].unsafe_reason}"
        writer(content)

        # 입력 메세지 삭제
        messages = state.get("messages", [])
        if messages:
            return {"messages": [RemoveMessage(id=messages[-1].id)]}
