from langgraph.graph import StateGraph, START, END

from app.agents.place_researcher.nodes import (
    PlaceResearcherAgent,
    PlaceResearcherTools,
    PlaceResponse,
)
from app.agents.place_researcher.edges import route_output
from app.agents.place_researcher.state import AgentState


from langgraph.checkpoint.memory import MemorySaver


def create_place_researcher_agent(verbose=True):
    flow = StateGraph(AgentState)
    flow.add_node("call_model", PlaceResearcherAgent(verbose=verbose))
    flow.add_node("tools", PlaceResearcherTools())
    flow.add_node("respond", PlaceResponse(verbose=verbose))

    flow.add_edge(START, "call_model")
    # Add a conditional edge to determine the next step after `call_model`
    flow.add_conditional_edges(
        "call_model",
        # After call_model finishes running, the next node(s) are scheduled
        # based on the output from route_model_output
        route_output,
    )

    # Add a normal edge from `tools` to `call_model`
    # This creates a cycle: after using tools, we always return to the model
    flow.add_edge("tools", "call_model")
    flow.add_edge("respond", END)

    memory = MemorySaver()
    # Compile the builder into an executable graph
    graph = flow.compile(
        name="place_researcher",
        interrupt_after=["respond"],
        checkpointer=memory,
    )
    return graph
