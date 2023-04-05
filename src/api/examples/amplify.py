from fvalues import F

from ice.recipe import recipe

from src.api.defs import Agent, ask, decompose, async_map


Question = str
Answer = str
Subs = list[tuple[Question, Answer]]


def render_background(subs: Subs) -> str:
    if not subs:
        return ""
    subs_text = F("\n\n").join(F(f"Q: {q}\nA: {a}") for (q, a) in subs)
    return subs_text


async def get_subs(question: str, depth: int) -> Subs:
    subquestions = await decompose(question, amount="2-5")
    subanswers = await async_map(
        subquestions, lambda q: amplify(question=q, depth=depth)
    )
    return list(zip(subquestions, subanswers))


async def amplify(
    question: str = "What is the effect of creatine on cognition?", depth: int = 1
):
    subs = await get_subs(question, depth - 1) if depth > 0 else []
    background_text = render_background(subs)
    answer = await ask(question, context=background_text)
    return answer
