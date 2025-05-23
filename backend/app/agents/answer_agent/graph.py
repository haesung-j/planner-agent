from langgraph.graph import StateGraph, START, END

from app.agents.answer_agent.nodes import AnswerAgent
from app.agents.answer_agent.state import AgentState


def create_answer_agent():
    flow = StateGraph(AgentState)
    flow.add_node("call_model", AnswerAgent())

    flow.add_edge(START, "call_model")
    flow.add_edge("call_model", END)

    # Compile the builder into an executable graph
    graph = flow.compile(name="answer_agent")
    return graph
