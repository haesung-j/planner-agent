from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from app.agents.google_tools import calendar_tools
from app.config import config


def create_calendar_chain(
    model_name: str, current_date: str, current_time: str
) -> RunnableSequence:
    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)
    prompt = load_prompt("app/prompts/calendar_agent.yaml").template

    model_with_tools = model.bind_tools(calendar_tools, parallel_tool_calls=False)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    prompt = prompt.partial(current_date=current_date, current_time=current_time)

    chain = prompt | model_with_tools

    return chain
