from app.agents.calendar_agent.nodes import CalendarAgent, CalendarTools
from langgraph.graph import StateGraph, START

from app.agents.calendar_agent.nodes import CalendarAgent
from app.agents.calendar_agent.edges import route_output
from app.agents.calendar_agent.state import AgentState


def create_calendar_agent(verbose=True):
    flow = StateGraph(AgentState)
    flow.add_node("call_model", CalendarAgent(verbose=verbose))
    flow.add_node("tools", CalendarTools())

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

    # Compile the builder into an executable graph
    graph = flow.compile(name="calendar_agent")
    return graph
