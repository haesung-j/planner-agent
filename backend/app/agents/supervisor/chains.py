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


class RouteResponse(BaseModel):
    reason: Annotated[str, "reason for the decision"]
    next: Annotated[
        AgentName,
        "next agent to route to. FINISH if the conversation should end.",
    ]
    exaplain: Annotated[str, "Explain to the user what you're going to do"]


def create_supervisor_chain(model_name: str) -> RunnableSequence:
    supervisor_system_prompt = load_prompt("app/prompts/supervisor.yaml").template

    supervisor_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", supervisor_system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? "
                "Or should we 'FINISH'? Select one of: {options}",
            ),
        ]
    )

    supervisor_prompt = supervisor_prompt.partial(
        options=str(options_for_next + ["FINISH"]),
        agents_description=get_agents_description(),
    )

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.1)

    model = model.with_structured_output(RouteResponse)
    supervisor_chain = supervisor_prompt | model
    return supervisor_chain
