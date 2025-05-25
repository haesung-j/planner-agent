from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from app.config import config


def create_message_chain(model_name: str, itinerary: str | None) -> RunnableSequence:
    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    elif model_name == "gpt-4.1-mini":
        model = ChatOpenAI(model=model_name, temperature=0.1)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    prompt = load_prompt("app/prompts/message_agent.yaml").template

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
            (
                "system",
                "If a travel itinerary has been completed, please organize and present the finalized itinerary content in a user-friendly format.\n{itinerary}",
            ),
        ]
    )

    prompt = prompt.partial(itinerary=itinerary)

    chain = prompt | model

    return chain
