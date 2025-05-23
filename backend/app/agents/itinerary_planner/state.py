from typing import Annotated, Sequence
from typing import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep


class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    itinerary: str
