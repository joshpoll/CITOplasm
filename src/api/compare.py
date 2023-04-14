from dataclasses import dataclass
from typing import Optional, Union

from fvalues import F
from src.api.agent import Agent
from src.api.cito import createCITO


@dataclass(frozen=True)
class SameAs:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are the same."


@dataclass(frozen=True)
class DifferentThan:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are different."


async def info_eq(text1: str, text2: str, agent: Optional[Agent] = None) -> bool:
    info_eq = createCITO(
        "Are these two pieces of information the same?",
        [SameAs, DifferentThan],
        agent=agent,
    )

    _, answer = await info_eq(
        F(
            f"""First piece of information: "{text1}"

Second piece of information: "{text2}"
    """
        ).strip()
    )
    return answer == SameAs()


@dataclass(frozen=True)
class LessThan:
    desc: Optional[
        str
    ] = "Choose this option if the first piece of information is less than the second piece of information."


@dataclass(frozen=True)
class GreaterThan:
    desc: Optional[
        str
    ] = "Choose this option if the first piece of information is greater than the second piece of information."


@dataclass(frozen=True)
class Incomparable:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are incomparable."


async def info_cmp(
    text1: str, text2: str, agent: Optional[Agent] = None
) -> Union[LessThan, SameAs, GreaterThan, Incomparable]:
    info_cmp = createCITO(
        "Which of these pieces of information is greater?",
        [LessThan, SameAs, GreaterThan, Incomparable],
        agent=agent,
    )

    _, answer = await info_cmp(
        F(
            f"""First piece of information: "{text1}"

Second piece of information: "{text2}"
    """.strip()
        )
    )
    return answer
