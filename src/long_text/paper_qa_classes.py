from fvalues import F

from ice.paper import Paper, Paragraph
from ice.recipe import recipe
from ice.utils import map_async
from src.qa import answer


def make_prompt(paragraph: Paragraph, question: str) -> str:
    return F(
        f"""
Here is a paragraph from a research paper: "{paragraph}"

Question: Does this paragraph answer the question '{question}'? Say Yes or No.
Answer:
"""
    ).strip()


# classify a paragraph, Yes/No
async def classify_paragraph(paragraph: Paragraph, question: str) -> float:
    choice_probs, _ = await recipe.agent().classify(
        prompt=make_prompt(paragraph, question),
        choices=(" Yes", " No"),
    )
    return choice_probs.get(" Yes", 0.0)


async def get_relevant_paragraphs(paper: Paper, question: str, top_n: int = 3):
    # get probabilities for each paragraph
    probs = await map_async(
        paper.paragraphs, lambda par: classify_paragraph(par, question)
    )
    # return top_n paragraphs
    sorted_pairs = sorted(
        zip(paper.paragraphs, probs), key=lambda pair: pair[1], reverse=True
    )
    return [par for par, prob in sorted_pairs[:top_n]]


async def answer_for_paper(paper: Paper, question: str):
    relevant_paragraphs = await get_relevant_paragraphs(paper, question)
    relevant_str = F("\n\n").join(str(p) for p in relevant_paragraphs)
    response = await answer(context=relevant_str, question=question)
    return response


recipe.main(answer_for_paper)
