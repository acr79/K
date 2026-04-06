"""Web search — DuckDuckGo by default (no API key), Tavily as upgrade."""

import os
from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "ddg"


def search(query: str, max_results: int = 8) -> list[SearchResult]:
    """Search the web. Uses Tavily if TAVILY_API_KEY is set, else DuckDuckGo."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if api_key:
        return _tavily_search(query, max_results, api_key)
    return _ddg_search(query, max_results)


def _ddg_search(query: str, max_results: int) -> list[SearchResult]:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        raise RuntimeError("Run: pip install duckduckgo-search")

    results = []
    with DDGS() as ddg:
        for r in ddg.text(query, max_results=max_results):
            results.append(SearchResult(
                title=r.get("title", ""),
                url=r.get("href", ""),
                snippet=r.get("body", ""),
                source="ddg"
            ))
    return results


def _tavily_search(query: str, max_results: int, api_key: str) -> list[SearchResult]:
    try:
        from tavily import TavilyClient
    except ImportError:
        raise RuntimeError("Run: pip install tavily-python")

    client = TavilyClient(api_key=api_key)
    response = client.search(query, max_results=max_results)
    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("content", ""),
            source="tavily"
        )
        for r in response.get("results", [])
    ]
