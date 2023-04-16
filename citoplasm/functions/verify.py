from dataclasses import dataclass
from typing import Optional, Union
from fvalues import F
from citoplasm.actions import CannotAnswer
from citoplasm.agent.agent import Agent

from citoplasm.cito import createCITO


@dataclass(frozen=True)
class Correct:
    desc: Optional[str] = "Choose this option if the answer is correct."


@dataclass(frozen=True)
class Wrong:
    desc: Optional[str] = "Choose this option if the answer is wrong."


async def verify(question: str, answer: str, agent: Optional[Agent] = None) -> bool:
    verify = createCITO(
        "Consider the potential answer to the question. Is it correct?",
        [Correct, Wrong, CannotAnswer],
        agent=agent,
    )

    thought, answer = await verify(
        F(
            f"""Question: "{question}"

Answer: "{answer}"
    """.strip()
        ),
    )

    return answer == Correct()
