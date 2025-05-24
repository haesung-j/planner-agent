from langgraph.graph import StateGraph, START

from app.agents.share_agent.nodes import ShareAgent, ShareTools
from app.agents.share_agent.edges import route_output
from app.agents.share_agent.state import AgentState
from langgraph.checkpoint.memory import MemorySaver


def create_share_agent(verbose=True, **kwargs):
    flow = StateGraph(AgentState)
    flow.add_node("call_model", ShareAgent(verbose=verbose))
    flow.add_node("tools", ShareTools())

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
    memory = kwargs.get("memory", False)
    if memory:
        graph = flow.compile(name="share_agent", checkpointer=MemorySaver())
        return graph

    graph = flow.compile(name="share_agent")
    return graph
