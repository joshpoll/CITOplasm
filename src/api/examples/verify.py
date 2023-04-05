from fvalues import F
from src.api.defs import classify


async def verify_answer(question: str, answer: str) -> bool:
    res = await classify(
        F(
            f"""Consider this question: "{question}"

Potential answer: "{answer}"
"""
        ),
        ["Yes", "No"],
        instructions="Consider the potential answer below. Is it correct?",
    )

    return res == "Yes"
