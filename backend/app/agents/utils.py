from typing import List
from app.agents.place_researcher.chains import PlaceInfo

from langchain_core.messages import BaseMessage


def places_to_readable_format(places: List[PlaceInfo]) -> str:
    result = []
    for i, place in enumerate(places, 1):
        result.append(f"recommanded place {i}: {place.name}")
        result.append(f"- address: {place.address}")
        result.append(f"- latitude: {place.latitude}")
        result.append(f"- longitude: {place.longitude}")
        result.append(f"- rating: {place.rating}")
        result.append(f"- place_id: {place.place_id}")
        result.append(f"- reason: {place.reason}")
        result.append("")
    return "\n".join(result)


def remove_tool_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    return [msg for msg in messages if msg.type != "tool"]


def format_places_to_string(places: list) -> str:

    if not places:
        return "선택된 장소가 없습니다."

    formatted_text = f"**선택된 장소 ({len(places)}개)**\n\n"

    for i, place in enumerate(places, 1):
        # 평점 표시 (별표 또는 숫자)
        rating_display = ""
        if place.rating and place.rating > 0:
            rating_display = place.rating
        else:
            rating_display = "평점 정보 없음"

        formatted_text += f"""**{i}. {place.name}**
- 주소: {place.address}
- 평점: {rating_display}
- 설명: {place.reason}

"""

    return formatted_text.strip()
