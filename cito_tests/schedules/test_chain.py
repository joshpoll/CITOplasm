import pytest
from citoplasm.actions import AnswerDirectly, CannotAnswer

from citoplasm.schedules.chain import createChain
from citoplasm.tools.search import Search


@pytest.mark.asyncio
async def test_chain():
    _chain = createChain(
        "Answer the question as best you can.",
        [Search],
        [AnswerDirectly, CannotAnswer],
    )
    res = await _chain("How many people live in canada as of 2023?", debug=True)
    print(res)
