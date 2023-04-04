import httpx

from fvalues import F

from ice.recipe import recipe
from src.tools.utils import *


def make_search_result_prompt(context: str, query: str, question: str) -> str:
    return F(
        f"""
Search results from Google for the query "{query}": "{context}"

Answer the following question, using the search results if helpful:

Question: "{question}"
Answer: "
"""
    ).strip()


def make_search_query_prompt(question: str) -> str:
    return F(
        f"""
You're trying to answer the question {question}. You get to type in a search query to Google, and then you'll be shown the results. What query do you want to search for?

Query: "
"""
    ).strip('" ')


async def choose_query(question: str) -> str:
    prompt = make_search_query_prompt(question)
    query = await recipe.agent().complete(prompt=prompt, stop='"')
    return query


async def answer_by_search(
    question: str = "Who is the president of the United States?",
) -> str:
    query = await choose_query(question)
    results = await search(query)
    results_str = render_results(results)
    prompt = make_search_result_prompt(results_str, query, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')
    return answer


recipe.main(answer_by_search)
