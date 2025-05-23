from typing import cast
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode
from datetime import datetime

from app.agents.calendar_agent.tools import calendar_tools
from app.config import config
from app.agents.calendar_agent.chains import create_calendar_chain
from app.agents.base import BaseNode


class CalendarAgent(BaseNode):
    def __init__(self, name: str = "CalendarAgent", **kwargs):
        super().__init__(name, **kwargs)
        self.model_name = config.CALENDAR_AGENT_MODEL

    async def arun(self, state):
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        chain = create_calendar_chain(self.model_name, current_date, current_time)

        response = cast(
            AIMessage,
            await chain.ainvoke(state.messages),
        )
        response.name = "calendar_agent"
        # 마지막 단계인데도 모델이 도구를 사용하려는 경우
        if state.is_last_step and response.tool_calls:
            return {
                "messages": [
                    AIMessage(
                        id=response.id,
                        content="죄송합니다. 질문에 대한 답변을 찾을 수 없습니다.",
                    )
                ]
            }
        return {"messages": [response]}


class CalendarTools(ToolNode):
    def __init__(self, **kwargs):
        super().__init__(tools=calendar_tools, name="calendar_tools", **kwargs)
