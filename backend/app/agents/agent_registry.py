from typing import Dict, List, Literal, TypedDict


class AgentInfo(TypedDict):
    description: str
    enabled: bool


# 모든 에이전트 정의 및 설명
AGENTS_REGISTRY: Dict[str, AgentInfo] = {
    "place_researcher": {
        "description": "specialized agent to search for places.",
        "enabled": True,
    },
    "calendar_agent": {
        "description": """
            specialized agent to create/read/update/delete an event in Google Calendar. 
            This agent can also process time-related information, such as the current date and time.
            
            ## STRICT CALENDAR TOOL USAGE RULES1. STRICT RULE: ONLY use calendar tools when the user EXPLICITLY makes a calendar-related query or request.

            2. Allowed Request Types:
                    - "What's my schedule tomorrow?"
                    - "Add a meeting on October 15th"
                    - "Show me my schedule for this week"
                    - "Cancel my appointment next Tuesday"

            3. Prohibited Scenarios:
                    - Conversations where user doesn't mention calendar
                    - Speculative calendar lookups for ambiguous questions
                    - Unsolicited calendar checks in unrelated contexts

            4. Guidelines for Uncertain Cases:
                - First clarify the user's intention explicitly
                - Request explicit permission: "Would you like me to check your calendar?"

            NEVER violate these rules. Unauthorized calendar tool usage is considered a serious privacy violation.
            """,
        "enabled": True,
    },
    "general_conversation": {
        "description": "specialized agent to have a general conversation with the user",
        "enabled": False,
    },
    "itinerary_planner": {
        "description": "specialized agent to create an itinerary plan. This agent is an agent that creates a itinerary based on a given set of places, so **it SHOULD ONLY be called when enough requirements have been collected from the other agents.**> ** DO NOT** invoke itinerary_planner directly if no prior search has occurred.",
        "enabled": False,
    },
}


# 활성화된 에이전트 목록 생성
def get_enabled_agents() -> List[str]:
    return [agent for agent, info in AGENTS_REGISTRY.items() if info["enabled"]]


# 에이전트 이름에 대한 Literal 타입 생성
options_for_next = get_enabled_agents() + ["FINISH"]
AgentName = Literal[tuple(options_for_next)]

# for conditional edges
options_for_next_dict = {agent: agent for agent in options_for_next}
options_for_next_dict["FINISH"] = "answer_agent"


# 프롬프트용 설명 문자열 생성
def get_agents_description() -> str:
    return "\n".join(
        [
            f"- {agent}: {info['description']}."
            for agent, info in AGENTS_REGISTRY.items()
            if info["enabled"]
        ]
    )
