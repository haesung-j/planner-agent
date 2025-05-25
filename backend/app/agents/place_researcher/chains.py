from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableSequence
from app.agents.place_researcher.tools import (
    web_search,
    search_place,
    get_place_details,
)
from app.config import config


class PlaceInfo(BaseModel):
    name: str = Field(description="The name of the place")
    address: str = Field(description="The address of the place")
    latitude: float = Field(description="The latitude of the place")
    longitude: float = Field(description="The longitude of the place")
    rating: float = Field(description="The rating of the place", ge=0, le=5)
    # reviews: Optional[list[str]] = Field(
    #     description="The reviews of the place. If you can't find any reviews, return an empty list."
    # )
    place_id: str = Field(description="The place_id of the place")
    reason: str = Field(
        description="Explain why this place is the best fit for the user's question compared to other places."
    )


class Recommendation(BaseModel):
    place_info: List[PlaceInfo] | None = Field(
        description="Information about recommended places", default=None
    )


def create_place_researcher_chain(model_name: str) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    elif model_name == "gemini-1.5-flash":
        model = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    tools = [
        # web_search,
        search_place,
        get_place_details,
    ]

    prompt = load_prompt("app/prompts/place_researcher.yaml").template

    model_with_tools = model.bind_tools(tools, parallel_tool_calls=False)

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


def create_place_researcher_response(model_name: str) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    model_with_structured_output = model.with_structured_output(Recommendation)
    return model_with_structured_output
