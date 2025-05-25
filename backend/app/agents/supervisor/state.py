from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from app.agents.agent_registry import options_for_next
from app.agents.guardrail.state import GuardrailOutput


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: Literal[*options_for_next]
    reason: str
    places: list[str]
    itinerary: str
    safety_check: GuardrailOutput
    selected_places: list
