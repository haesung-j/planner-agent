from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from app.config import config


class ItineraryInformation(BaseModel):
    """Information about the itinerary."""

    places: str = Field(description="Places to visit")
    dates: str = Field(description="Dates to visit")
    days: int = Field(description="Number of days to stay")


def create_itinerary_info_gather_chain(
    model_name: str, places: Any
) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)

    model = model.bind_tools([ItineraryInformation])

    prompt = load_prompt("app/prompts/itinerary_gather.yaml").template

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    prompt = prompt.partial(
        current_date=datetime.now().strftime("%Y-%m-%d"),
        current_time=datetime.now().strftime("%H:%M:%S"),
        places=places,
    )

    chain = prompt | model

    return chain


def create_itinerary_planner_chain(model_name: str) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)

    prompt = load_prompt("app/prompts/itinerary_planner.yaml").template

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

    chain = prompt | model

    return chain
