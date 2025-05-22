from langgraph.graph import StateGraph, START, END

from app.agents.supervisor.nodes import Supervisor
from app.agents.supervisor.state import State


def create_supervisor():
    flow = StateGraph(State)
    flow.add_node("supervisor", Supervisor())

    flow.add_edge(START, "supervisor")
    flow.add_edge("supervisor", END)

    # Compile the builder into an executable graph
    graph = flow.compile(name="supervisor")
    return graph
