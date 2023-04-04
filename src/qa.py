from fvalues import F
from ice.recipe import recipe

DEFAULT_CONTEXT = "We're running a hackathon on 9/9/2022 to decompose complex reasoning tasks into subtasks that are easier to automate & evaluate with language models. Our team is currently breaking down reasoning about the quality of evidence in randomized controlled trials into smaller tasks e.g. placebo, intervention adherence rate, blinding procedure, etc."
DEFAULT_QUESTION = "What is happening on 9/9/2022?"


def make_qa_prompt(context: str, question: str) -> str:
    return F(
        f"""
Background text: "{context}"

Answer the following question about the background text above:

Question: "{question}"
Answer: "
"""
    ).strip()


def make_cot_qa_prompt(context: str, question: str) -> str:
    return F(
        f"""
Background text: "{context}"

Answer the following question about the background text above:

Question: "{question}"
Answer: Let's think step by step. "
"""
    ).strip()


# more specific, more accurate, or more concise


def make_reflection_prompt(context: str, question: str, prev_answer: str) -> str:
    return F(
        f"""
Background text: "{context}"

Question: "{question}"

Please improve the previous answer to the question by making it more specific, more accurate, and
more concise. If you cannot do so, return the previous answer. Think step by step.

Previous Answer: "{prev_answer}"
Answer: "
"""
    ).strip()


async def answer(
    context: str = DEFAULT_CONTEXT, question: str = DEFAULT_QUESTION
) -> str:
    prompt = make_cot_qa_prompt(context, question)
    answer = await recipe.agent().complete(prompt=prompt, stop='"')

    prev_answer = ""
    improved_answer = answer
    max_iterations = 5
    while prev_answer != improved_answer and max_iterations > 0:
        prev_answer = improved_answer
        improved_answer = await recipe.agent().complete(
            prompt=make_reflection_prompt(context, question, prev_answer), stop='"'
        )
        max_iterations -= 1

    return improved_answer


recipe.main(answer)
