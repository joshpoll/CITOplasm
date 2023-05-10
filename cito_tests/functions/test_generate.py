import pytest
from citoplasm.functions.generate import CannotAnswer, ItemList, generate
from citoplasm.functions.ask import ask
from citoplasm.functions.compare import MoreInformative, SimilarTo, info_cmp, info_eq


@pytest.mark.asyncio
async def test_generate_countries():
    answer = await generate(5, "countries")
    print(answer)
    assert isinstance(answer, ItemList) and len(answer.items) == 5
    # TODO: check that they're countries!


@pytest.mark.asyncio
async def test_generate_with_context():
    answer = await generate("2-5", "related facts", context="Fact: The sky is blue.")
    print(answer)
    assert (
        isinstance(answer, ItemList)
        and len(answer.items) >= 2
        and len(answer.items) <= 5
    )
    # TODO: how do I check that they're related to the context?


@pytest.mark.asyncio
async def test_generate_cannot_answer():
    answer = await generate(10, "core members of the Beatles")
    print(answer)
    assert isinstance(answer, CannotAnswer)
    # TODO: check that the reason is correct!
