from dataclasses import dataclass, fields
from typing import Any
import pytest

from citoplasm.functions.chain import chain, AnswerDirectly
from citoplasm.functions.compare import MoreInformative, SameAs, info_cmp, info_eq
from citoplasm.tools.python import Python
from citoplasm.tools.search import Search, search


@pytest.mark.asyncio
async def test_chain():
    res = await chain("How many people live in canada as of 2023?", [Search])
    # https://www.reuters.com/world/americas/record-international-migration-spurs-historic-rise-canadian-population-2023-03-22/
    print(res)
    comparison = await info_cmp(res, "1 million")
    assert isinstance(comparison, SameAs) or isinstance(comparison, MoreInformative)


# TODO: I should verify this with multi-step LLM verification
@pytest.mark.asyncio
async def test_chain_multistep():
    res = await chain(
        "What is the log10 of the number of people living in the US vs China?",
        [Search, Python],
    )
    print(res)
    comparison = await info_eq(
        res,
        "The log10 of the population of the US is 8.52 and the log10 of the population of China is 9.16.",
    )
    assert isinstance(comparison, SameAs) or isinstance(comparison, MoreInformative)


# TODO: I should verify this with multi-step LLM verification
@pytest.mark.asyncio
async def test_chain_departed():
    res = await chain(
        "In what year was the film Departed with Leonardo DiCaprio released? What is this year raised to the 0.43 power?",
        [Search, Python],
    )
    print(res)
    comparison = await info_cmp(
        res,
        "2006 raised to the power of 0.43 is approximately 26.30.",
    )
    assert isinstance(comparison, SameAs) or isinstance(comparison, MoreInformative)
