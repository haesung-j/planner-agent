from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, load_prompt
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel
from typing import Annotated, TypedDict
from app.agents.agent_registry import (
    options_for_next,
    get_agents_description,
    AgentName,
)
from langchain_google_genai import ChatGoogleGenerativeAI


class RouteResponse(BaseModel):
    reason: Annotated[str, "reason for the decision"]
    next: Annotated[
        AgentName,
        "next agent to route to. To get a response from the user, return the itinerary_planner.",
    ]
    notification: Annotated[
        str,
        "Notification to display to the user. Write the message 'Calling agent name...' to indicate which agent was called.",
    ]


def create_supervisor_chain(model_name: str) -> RunnableSequence:
    supervisor_system_prompt = load_prompt("app/prompts/supervisor.yaml").template

    supervisor_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", supervisor_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? "
                "Select one of: {options}",
            ),
        ]
    )

    supervisor_prompt = supervisor_prompt.partial(
        options=str(options_for_next),
        agents_description=get_agents_description(),
    )

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    elif model_name == "gemini-1.5-flash":
        model = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.1)

    model = model.with_structured_output(RouteResponse)
    supervisor_chain = supervisor_prompt | model
    return supervisor_chain
