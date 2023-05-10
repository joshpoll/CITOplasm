import pytest
from citoplasm.functions.verify import verify


@pytest.mark.asyncio
async def test_verify_easy_true():
    answer = await verify("What is 2 + 2?", "4")
    assert answer


@pytest.mark.asyncio
async def test_verify_easy_false():
    answer = await verify("What is 2 + 2?", "5")
    assert not answer


@pytest.mark.asyncio
async def test_verify_medium_false():
    answer = await verify("What is the capital of Germany?", "Munich")
    assert not answer


@pytest.mark.asyncio
async def test_verify_medium_true():
    answer = await verify("What is the capital of Germany?", "Berlin")
    assert answer


# @pytest.mark.asyncio
# async def test_verify_hard_true():
#     answer = await verify(
#         "Beth bakes 4x 2 dozen batches of cookies in a week. If these cookies are shared amongst 16 people equally, how many cookies does each person consume?",
#         "6",
#     )
#     assert answer


# @pytest.mark.asyncio
# async def test_verify_hard_false():
#     answer = await verify(
#         "Beth bakes 4x 2 dozen batches of cookies in a week. If these cookies are shared amongst 16 people equally, how many cookies does each person consume?",
#         "12",
#     )
#     assert not answer
