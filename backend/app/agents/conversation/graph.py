from langgraph.graph import StateGraph, START, END

from app.agents.conversation.nodes import GeneralConversation
from app.agents.conversation.state import AgentState


def create_conversation_agent():
    flow = StateGraph(AgentState)
    flow.add_node("call_model", GeneralConversation())

    flow.add_edge(START, "call_model")
    flow.add_edge("call_model", END)

    # Compile the builder into an executable graph
    graph = flow.compile(name="general_conversation")
    return graph
