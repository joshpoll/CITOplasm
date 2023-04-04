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


recipe.main(search)
