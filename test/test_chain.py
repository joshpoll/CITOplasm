from dataclasses import dataclass, fields
from typing import Any
import pytest
from src.api.classify import classify, pretty_print_option

from src.api.examples.chain import chain, FinalAnswer
from src.tools.search_string import search_string
from test.approx_cmp import approx_eq


@dataclass(frozen=True)
class Search:
    query: str
    desc: str = "Search Google for the given query"

    def run(self) -> Any:
        return search_string(self.query)


@pytest.mark.asyncio
async def test_chain():
    res = await classify(
        "How many people live in Germany?",
        "You want to answer the question.",
        [Search],
    )
    res = await chain("How many people live in canada as of 2023?", [Search])
    # https://www.reuters.com/world/americas/record-international-migration-spurs-historic-rise-canadian-population-2023-03-22/
    assert await approx_eq(res, "39.57 million")
