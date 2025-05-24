from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from app.agents.google_tools import gmail_tools
from app.config import config


def create_share_chain(model_name: str, travel_itinerary: str) -> RunnableSequence:
    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    prompt = load_prompt("app/prompts/share_agent.yaml").template

    model_with_tools = model.bind_tools(gmail_tools)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
            (
                "system",
                """You must share your travel itinerary below. If not given below, ask the user to create a travel itinerary first.""",
            ),
            MessagesPlaceholder("travel_itinerary"),
        ]
    )

    prompt = prompt.partial(travel_itinerary=travel_itinerary)

    chain = prompt | model_with_tools

    return chain
