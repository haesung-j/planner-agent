from langgraph.graph import StateGraph, START, END

from app.agents.message_agent.nodes import MessageAgent
from app.agents.message_agent.state import AgentState


def create_message_agent(verbose=True):
    flow = StateGraph(AgentState)
    flow.add_node("call_model", MessageAgent(verbose=verbose))

    flow.add_edge(START, "call_model")
    flow.add_edge("call_model", END)

    # Compile the builder into an executable graph
    graph = flow.compile(name="message_agent")
    return graph
