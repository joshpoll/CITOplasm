import pytest
from src.api.examples.qa import *

from test.approx_cmp import approx_eq, approx_gt


@pytest.mark.asyncio
async def test_qa():
    answer = await qa("What is happening on 9/9/2022?")
    assert await approx_eq(answer, "I don't know.")


@pytest.mark.asyncio
async def test_qa_with_context():
    answer = await qa_with_context(
        "What is happening on 9/9/2022?",
        "We're running a hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models. Our team is currently breaking down reasoning about the quality of evidence in randomized controlled trials into smaller tasks e.g. placebo, intervention adherence rate, blinding procedure, etc.",
    )
    assert await approx_gt(answer, "A hackathon is happening on 9/9/2022.")
