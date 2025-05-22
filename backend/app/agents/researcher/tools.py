from typing import Annotated, Any, Optional, cast
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_community.tools.tavily_search import TavilySearchResults


@tool(parse_docstring=True)
async def search(query: str) -> Optional[list[dict[str, Any]]]:
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
