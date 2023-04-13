from fvalues import F
from src.api.classify import *


@dataclass(frozen=True)
class Yes(BaseOption):
    desc: Optional[str] = None


@dataclass(frozen=True)
class No(BaseOption):
    desc: Optional[str] = None


async def verify_answer(question: str, answer: str) -> bool:
    res = await classify(
        F(
            f"""Consider this question: "{question}"

Potential answer: "{answer}"
"""
        ),
        "Consider the potential answer to the question. Is it correct?",
        [Yes, No],
    )

    return res == Yes()
