from typing import Annotated, Sequence
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep


class AgentState(BaseModel):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    is_last_step: IsLastStep = Field(default=False)
