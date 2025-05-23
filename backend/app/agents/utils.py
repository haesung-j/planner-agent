from typing import List
from app.agents.place_researcher.chains import PlaceInfo


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
