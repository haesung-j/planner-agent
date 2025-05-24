from typing import Literal
from langchain_core.messages import AIMessage


def route_output(state) -> Literal["__end__", "tools"]:
    """
    Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.get("messages", [])[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # If there is no tool call, finish
    if not last_message.tool_calls:
        return "__end__"
    return "tools"
