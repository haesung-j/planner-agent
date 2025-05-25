import os
import googlemaps
from typing import Annotated, Any, Optional, cast
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_community.tools.tavily_search import TavilySearchResults

from app.config import config


client = googlemaps.Client(key=config.GOOGLE_MAP_API_KEY)


@tool(parse_docstring=True)
async def web_search(query: str) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    Args:
      query: The query to search for.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for finding information on a wide range of topics.
    """
    # configuration = Configuration.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=5)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)


@tool(parse_docstring=True)
def search_place(query: str) -> str:
    """
    Searches for places using the Google Places API based on a natural language query.

    This function allows for text-based searches of places, businesses, and points of interest
    using the Google Maps Platform. It accepts natural language queries and returns up to 5
    place results that match the search criteria. For better results, use general category
    terms rather than specific business names.

    Args:
        query: A string containing the search query. Recommended to use general terms
              for broader results (e.g., 'Gangnam cafe', 'Hongdae restaurant', 'Seoul museum')
              rather than specific business names.

    Returns:
        A list of up to 5 places matching the query, including basic information such as name,
        address, rating, and most importantly the place_id which can be used with
        get_place_reviews to retrieve more detailed information.

    Usage example:
        search_place("Hongdae cafe")  # Returns multiple cafe options in Hongdae area
        search_place("Seoul traditional restaurant")  # Returns various traditional restaurants
    """
    response = client.places(query=query, language="ko")
    places = []
    # Limit results to 5 places
    for result in response.get("results", [])[:5]:
        place = {
            "id": result.get("place_id", f"{result.get('name', '')}"),
            "name": result.get("name", ""),
            "address": result.get("formatted_address", ""),
            "latitude": result.get("geometry", {}).get("location", {}).get("lat", 0),
            "longitude": result.get("geometry", {}).get("location", {}).get("lng", 0),
            "rating": result.get("rating", 0),
        }
        places.append(place)
    return places


@tool(parse_docstring=True)
def get_place_details(place_id: str) -> str:
    """
    Retrieves detailed information and reviews for a specific place using the Google Maps API.

    This function uses a place_id (previously obtained from the search_place tool) to fetch
    comprehensive details about a location, including its address, contact information,
    business hours, website URL, and user reviews.

    Args:
        place_id: A string that uniquely identifies a place in the Google Maps API
                 (e.g., 'ChIJN1t_tDeuEmsRUsoyG83frY4')

    Returns:
        Detailed information about the place including name, address, rating, review content,
        photo references, opening hours, and other available details.

    Usage example:
        1. Use search_place to query '서울역 레스토랑' to get a place_id
        2. Use get_place_reviews with that place_id to retrieve detailed information and reviews
    """
    return client.place(place_id=place_id, language="ko")
