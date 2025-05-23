from langgraph.graph import StateGraph, START, END

from app.agents.itinerary_planner.nodes import (
    ItineraryPlannerAgent,
    ItineraryInformationGatherer,
    add_tool_message,
)

from app.agents.itinerary_planner.state import AgentState
from app.agents.itinerary_planner.edges import get_state
from langgraph.checkpoint.memory import MemorySaver


def create_itinerary_planner_agent():
    flow = StateGraph(AgentState)
    flow.add_node("gather_info", ItineraryInformationGatherer())
    flow.add_node("generate_itinerary", ItineraryPlannerAgent())
    flow.add_node("add_tool_message", add_tool_message)

    flow.add_edge(START, "gather_info")
    flow.add_conditional_edges(
        "gather_info",
        get_state,
        {
            "add_tool_message": "add_tool_message",
            END: END,
        },
    )
    flow.add_edge("add_tool_message", "generate_itinerary")
    flow.add_edge("generate_itinerary", END)

    # memory = MemorySaver()
    graph = flow.compile(name="itinerary_planner")
    return graph
