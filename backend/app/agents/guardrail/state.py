from typing import Annotated, Sequence, TypedDict, Literal
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class GuardrailOutput(BaseModel):
    safety_check: Literal["safe", "unsafe"]
    unsafe_code: str
    unsafe_reason: str


class GuardrailState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    safety_check: GuardrailOutput
