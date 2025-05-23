from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.supervisor.nodes import Supervisor
from app.agents.supervisor.state import State
from app.agents.supervisor.edges import get_next
from app.agents.agent_registry import options_for_next_dict

from app.agents.answer_agent.graph import create_answer_agent
from app.agents.place_researcher.graph import create_place_researcher_agent
from app.agents.calendar_agent.graph import create_calendar_agent


def create_graph():
    answer_agent = create_answer_agent()
    place_researcher_agent = create_place_researcher_agent()
    calendar_agent = create_calendar_agent()

    flow = StateGraph(State)
    flow.add_node("supervisor", Supervisor())
    flow.add_node(answer_agent.name, answer_agent)
    flow.add_node(place_researcher_agent.name, place_researcher_agent)
    flow.add_node(calendar_agent.name, calendar_agent)

    flow.add_edge(START, "supervisor")
    flow.add_conditional_edges("supervisor", get_next, options_for_next_dict)
    flow.add_edge(place_researcher_agent.name, "supervisor")
    flow.add_edge(calendar_agent.name, "supervisor")
    flow.add_edge(answer_agent.name, END)

    memory = MemorySaver()
    graph = flow.compile(checkpointer=memory)
    return graph
