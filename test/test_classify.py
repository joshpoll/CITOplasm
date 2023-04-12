import pytest
from src.api.classify import *
from test.approx_cmp import approx_eq


@dataclass(frozen=True)
class Yes(BaseOption):
    desc: Optional[str] = None


@dataclass(frozen=True)
class No(BaseOption):
    desc: Optional[str] = None


@pytest.mark.asyncio
async def test_classify():
    res = await classify("2 + 2 = 4?", "Select an option.", [Yes, No])
    assert res == Yes()


@dataclass(frozen=True)
class AnswerDirectly(BaseOption):
    answer: str
    desc: str = "You provide your answer directly"


@dataclass(frozen=True)
class Search(BaseOption):
    query: str
    desc: str = "Search Google for the given query"


@dataclass(frozen=True)
class Python(BaseOption):
    expr: str
    desc: str = "Run the given expr in a Python REPL"


@pytest.mark.asyncio
async def test_choose_action_once_answer_directly_cot():
    # used to require Python, but now it's AnswerDirectly b/c of CoT
    res = await classify(
        "sqrt(2^8)?",
        "You want to answer the question.",
        [AnswerDirectly, Search, Python],
    )
    assert isinstance(res, AnswerDirectly)
    assert res.answer == "16"


@pytest.mark.asyncio
async def test_choose_action_once_python():
    res = await classify(
        "log10(3673378278273)?",
        "You want to answer the question.",
        [AnswerDirectly, Search, Python],
    )
    assert isinstance(res, Python)
    assert approx_eq(res.expr, "log10(3673378278273)")


@pytest.mark.asyncio
async def test_choose_action_once_search():
    res = await classify(
        "How many people live in Germany?",
        "You want to answer the question.",
        [AnswerDirectly, Search, Python],
    )
    assert isinstance(res, Search)
    # use approx_eq for the field
    assert await approx_eq(res.query, "How many people live in Germany?")


@pytest.mark.asyncio
async def test_choose_action_once_answer_directly():
    res = await classify(
        "2 + 2?",
        "You want to answer the question.",
        [AnswerDirectly, Search, Python],
    )
    assert isinstance(res, AnswerDirectly)
    assert await approx_eq(res.answer, "4")
