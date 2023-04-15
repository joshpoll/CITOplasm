from dataclasses import dataclass
import os
from typing import Any, List, Union
import httpx

from fvalues import F

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


async def search_json(
    query: str = "Who is the president of the United States?",
) -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": SERPAPI_API_KEY}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()


def render_results(data: dict) -> Union[str, List[str]]:
    if not data or not data.get("organic_results"):
        return "No results found"

    results = []
    for result in data["organic_results"]:
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet")
        if not title or not link or not snippet:
            continue
        results.append(str(F(f"{title}\n{link}\n{snippet}\n")))

    # return results[:3]
    return results[0]


async def search(
    question: str = "Who is the president of the United States?",
) -> Union[str, List[str]]:
    results = await search_json(question)
    return render_results(results)


@dataclass(frozen=True)
class Search:
    query: str
    desc: str = "Search Google for the given query"

    async def run(self) -> Any:
        return await search(self.query)
