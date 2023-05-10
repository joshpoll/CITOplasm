import pytest
from citoplasm.functions.decompose import decompose
from citoplasm.functions.decompose import CannotAnswer, ItemList
from citoplasm.functions.ask import ask
from citoplasm.functions.compare import MoreInformative, SimilarTo, info_cmp, info_eq


@pytest.mark.asyncio
async def test_decompose():
    answer = await decompose(5, "What is the population of the US?")
    print(answer)
    assert isinstance(answer, ItemList) and len(answer.items) == 5


@pytest.mark.asyncio
async def test_decompose_animals():
    answer = await decompose("2-5", "animals")
    print(answer)
    assert (
        isinstance(answer, ItemList)
        and len(answer.items) >= 2
        and len(answer.items) <= 5
    )
