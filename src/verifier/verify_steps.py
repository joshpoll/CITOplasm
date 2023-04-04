from fvalues import F

from ice.recipe import recipe
from src.verifier.utils import *
from ice.utils import map_async


def make_verification_prompt(question: str, steps: list[str]) -> str:
    return F(
        f"""Consider this question: "{question}"

Here are the first few steps of an answer:

{render_steps(steps)}

Q: Is step {len(steps)} correct, assuming that the previous steps are correct? Say "A: Yes" or "A: No".
A:"""
    )


async def check_step(question: str, steps: list[str]) -> float:
    """
    Return the probability that the step is correct
    """
    prompt = make_verification_prompt(question=question, steps=steps)
    answer_probs, _ = await recipe.agent().classify(
        prompt=prompt, choices=(" Yes", " No")
    )
    return answer_probs.get(" Yes", 0.0)


async def verify_answer(
    question: str = DEFAULT_QUESTION, steps: list[str] = DEFAULT_STEPS
):
    """
    For each prefix of 1..n steps, check if the nth step is correct.
    """
    step_indices = list(range(1, len(steps) + 1))
    step_probs = await map_async(
        step_indices, lambda i: check_step(question, steps[:i])
    )
    return list(zip(step_probs, steps))


recipe.main(verify_answer)

# Our confidence in the answer is still incredibly low (~20%).
# To increase this we can both give the model access to tools as well as creating subquestions where
# it is unsure. A calculator would be immensely helpful for the default task.
