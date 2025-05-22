from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from app.agents.agent_registry import AgentName, options_for_next


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: Literal[*options_for_next]
    reason: str
    # answer: str
