# https://python.langchain.com/en/latest/modules/chains/generic/sequential_chains.html

from fvalues import F
import pytest
from citoplasm.actions import AnswerDirectly, CannotAnswer

from citoplasm.cito import createCITO


@pytest.mark.asyncio
async def test_synopsis_review_simple():
    synopsis_cito = createCITO(
        """You are a playwright. Given the title of a play, it is your job to write a synopsis for that title. The synopsis should be three paragraphs long.""",
        [AnswerDirectly, CannotAnswer],
    )

    review_cito = createCITO(
        """You are a play critic from the New York Times. Given a synopsis of a play, it is your job to write a review for that play.""",
        [AnswerDirectly, CannotAnswer],
    )

    title = "Tragedy at Sunset on the Beach"

    _, synopsis = await synopsis_cito(
        F(
            f"""Title: "{title}"
""".strip()
        ),
    )

    _, review = await review_cito(
        F(
            f"""Synopsis: "{synopsis}"
    """.strip()
        ),
    )

    print(synopsis)
    print(review)
