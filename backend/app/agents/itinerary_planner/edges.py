from langgraph.graph import END

from langchain_core.messages import AIMessage


def get_state(state):
    messages = state["messages"]
    if isinstance(messages[-1], AIMessage) and messages[-1].tool_calls:
        return "add_tool_message"
    return END
