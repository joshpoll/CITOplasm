from dataclasses import dataclass
from typing import Optional
import pytest
from citoplasm.tools.python import Calculate, Python
from citoplasm.tools.search import Search

# TODO: update this to use cito


@dataclass(frozen=True)
class Yes:
    desc: Optional[str] = None


@dataclass(frozen=True)
class No:
    desc: Optional[str] = None


# @pytest.mark.asyncio
# async def test_classify():
#     res = await classify("2 + 2 = 4?", "Select an option.", [Yes, No])
#     assert res == Yes()


# @dataclass(frozen=True)
# class AnswerDirectly(BaseOption):
#     answer: str
#     desc: str = "You provide your answer directly"


# @pytest.mark.asyncio
# async def test_choose_action_once_answer_directly_cot():
#     # used to require Python, but now it's AnswerDirectly b/c of CoT
#     res = await classify(
#         "sqrt(2^8)?",
#         "You want to answer the question.",
#         [AnswerDirectly, Search, Python, Calculate],
#     )
#     # assert isinstance(res, AnswerDirectly)
#     # assert await approx_eq(res.answer, "16")
#     assert isinstance(res, Calculate)
#     assert await approx_eq(res.expr, "math.sqrt(2**8)")


# @pytest.mark.asyncio
# async def test_choose_action_once_python():
#     res = await classify(
#         "log10(3673378278273)?",
#         "You want to answer the question.",
#         [AnswerDirectly, Search, Python, Calculate],
#     )
#     assert isinstance(res, Calculate)
#     assert await approx_eq(res.expr, "log10(3673378278273)")


# @pytest.mark.asyncio
# async def test_choose_action_once_search():
#     res = await classify(
#         "How many people live in Germany?",
#         "You want to answer the question.",
#         [AnswerDirectly, Search, Python],
#     )
#     assert isinstance(res, Search)
#     # use approx_eq for the field
#     assert await approx_eq(res.query, "How many people live in Germany?")


# @pytest.mark.asyncio
# async def test_choose_action_once_answer_directly():
#     res = await classify(
#         "2 + 2?",
#         "You want to answer the question.",
#         [AnswerDirectly, Search, Python, Calculate],
#     )

#     error_path1 = None
#     error_path2 = None

#     try:
#         assert isinstance(res, AnswerDirectly)
#         assert await approx_eq(res.answer, "4")
#     except AssertionError as e:
#         error_path1 = e

#     try:
#         assert isinstance(res, Calculate)
#         assert await approx_eq(res.expr, "2 + 2")
#     except AssertionError as e:
#         error_path2 = e

#     if error_path1 and error_path2:
#         pytest.fail(
#             f"Both assertion paths failed:\nPath 1: {error_path1}\nPath 2: {error_path2}"
#         )
