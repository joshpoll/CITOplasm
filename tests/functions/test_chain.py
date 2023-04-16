from dataclasses import dataclass, fields
from typing import Any
import pytest

from citoplasm.functions.chain import chain, AnswerDirectly
from citoplasm.functions.compare import MoreInformative, info_cmp, info_eq
from citoplasm.tools.python import Python
from citoplasm.tools.search import Search, search


@pytest.mark.asyncio
async def test_chain():
    res = await chain("How many people live in canada as of 2023?", [Search])
    assert await info_eq(res, "30-40 million")


@pytest.mark.asyncio
async def test_chain_multistep():
    res = await chain(
        "What is the log10 of the number of people living in the US vs China?",
        [Search, Python],
        debug=True,
    )
    assert (
        await info_eq(
            res,
            "The log10 of the population of the US is 8.52 and the log10 of the population of China is 9.16.",
        )
    ) or (await info_eq(res, "0.64"))


@pytest.mark.asyncio
async def test_chain_departed():
    res = await chain(
        "In what year was the film Departed with Leonardo DiCaprio released? What is this year raised to the 0.43 power?",
        [Search, Python],
    )
    assert await info_eq(
        res,
        "2006 raised to the power of 0.43 is approximately 26.30.",
    )
