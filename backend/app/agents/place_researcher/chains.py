from datetime import datetime
from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from app.agents.place_researcher.tools import (
    web_search,
    search_place,
    get_place_reviews,
)
from app.config import config


def create_place_researcher_chain(model_name: str) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    tools = [
        web_search,
        search_place,
        # get_place_reviews
    ]

    prompt = load_prompt("app/prompts/place_researcher.yaml").template

    model_with_tools = model.bind_tools(tools)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    prompt = prompt.partial(
        current_date=datetime.now().strftime("%Y-%m-%d"),
        current_time=datetime.now().strftime("%H:%M:%S"),
    )

    chain = prompt | model_with_tools

    return chain
