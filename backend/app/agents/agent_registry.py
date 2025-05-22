from typing import Dict, List, Literal, TypedDict


class AgentInfo(TypedDict):
    description: str
    enabled: bool


# 모든 에이전트 정의 및 설명
AGENTS_REGISTRY: Dict[str, AgentInfo] = {
    "place_researcher": {
        "description": "specialized agent to search for places and get more information about them",
        "enabled": True,
    },
    "calendar_agent": {
        "description": "specialized agent to create/read/update/delete an event in Google Calendar",
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
options_for_next_dict["FINISH"] = "answer"


# 프롬프트용 설명 문자열 생성
def get_agents_description() -> str:
    return "\n".join(
        [
            f"- {agent}: {info['description']}."
            for agent, info in AGENTS_REGISTRY.items()
            if info["enabled"]
        ]
    )
