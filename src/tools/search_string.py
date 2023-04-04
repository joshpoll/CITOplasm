import os
import httpx

from fvalues import F

from ice.recipe import recipe

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def make_qa_prompt(context: str, question: str) -> str:
    return F(
        f"""
Background text: "{context}"

Answer the following question about the background text above:

Question: "{question}"
Answer: "
"""
    ).strip()


async def search(query: str = "Who is the president of the United States?") -> dict:
    async with httpx.AsyncClient() as client:
        params = {"q": query, "hl": "en", "gl": "us", "api_key": SERPAPI_API_KEY}
        response = await client.get("https://serpapi.com/search", params=params)
        return response.json()


def render_results(data: dict) -> str:
    if not data or not data.get("organic_results"):
        return "No results found"

    results = []
    for result in data["organic_results"]:
        title = result.get("title")
        link = result.get("link")
        snippet = result.get("snippet")
        if not title or not link or not snippet:
            continue
        results.append(F(f"{title}\n{link}\n{snippet}\n"))

    return F("\n").join(results)


async def search_string(
    question: str = "Who is the president of the United States?",
) -> str:
    results = await search(question)
    return render_results(results)


recipe.main(search_string)
