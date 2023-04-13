from dataclasses import dataclass, fields
from typing import Any
import pytest
from src.api.classify import classify, pretty_print_option

from src.api.examples.chain import chain, AnswerDirectly
from src.api.examples.tools.python import Python
from src.api.examples.tools.search import Search, search
from test.approx_cmp import approx_eq, approx_gt


@pytest.mark.asyncio
async def test_chain():
    res = await chain("How many people live in canada as of 2023?", [Search])
    # https://www.reuters.com/world/americas/record-international-migration-spurs-historic-rise-canadian-population-2023-03-22/
    assert await approx_gt(res, "39.57 million")


# TODO: I should verify this with multi-step LLM verification
@pytest.mark.asyncio
async def test_chain_multistep():
    res = await chain(
        "What is the log10 of the number of people living in the US vs China?",
        [Search, Python],
    )
    print(res)
    assert await approx_eq(
        res,
        "The log10 of the population of the US is 8.52 and the log10 of the population of China is 9.16.",
    )
