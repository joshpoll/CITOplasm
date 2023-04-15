import pytest
from citoplasm.functions.ask import ask
from citoplasm.functions.compare import MoreInformative, SameAs, info_cmp, info_eq


@pytest.mark.asyncio
async def test_ask():
    answer = await ask("What is happening on 9/9/2022?")
    assert await info_eq(answer, "I don't know.")


@pytest.mark.asyncio
async def test_ask_with_context():
    answer = await ask(
        "What is happening on 9/9/2022?",
        context="We're running a hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models. Our team is currently breaking down reasoning about the quality of evidence in randomized controlled trials into smaller tasks e.g. placebo, intervention adherence rate, blinding procedure, etc.",
    )
    res = await info_cmp(answer, "A hackathon is happening on 9/9/2022.")
    assert isinstance(res, MoreInformative) or isinstance(res, SameAs)
