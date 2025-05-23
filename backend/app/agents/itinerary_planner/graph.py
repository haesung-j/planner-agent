from langgraph.graph import StateGraph, START, END

from app.agents.itinerary_planner.nodes import (
    ItineraryPlannerAgent,
)

# from app.agents.itinerary_planner.edges import route_output
from app.agents.itinerary_planner.state import AgentState


from langgraph.checkpoint.memory import MemorySaver


def create_itinerary_planner_agent():
    flow = StateGraph(AgentState)
    flow.add_node("call_model", ItineraryPlannerAgent())
    # flow.add_node("tools", PlaceResearcherTools())
    # flow.add_node("respond", PlaceResponse())

    flow.add_edge(START, "call_model")
    # Add a conditional edge to determine the next step after `call_model`
    # flow.add_conditional_edges(
    #     "call_model",
    #     # After call_model finishes running, the next node(s) are scheduled
    #     # based on the output from route_model_output
    #     route_output,
    # )

    # Add a normal edge from `tools` to `call_model`
    # This creates a cycle: after using tools, we always return to the model
    # flow.add_edge("tools", "call_model")
    flow.add_edge("call_model", END)

    memory = MemorySaver()
    # Compile the builder into an executable graph
    graph = flow.compile(name="itinerary_planner", checkpointer=memory)
    return graph
