from dataclasses import dataclass
from typing import Optional, Union

from fvalues import F
from citoplasm.agent.agent import Agent
from citoplasm.cito import createCITO


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


async def info_eq(
    text1: str, text2: str, agent: Optional[Agent] = None, debug: bool = False
) -> bool:
    info_eq = createCITO(
        "Are these two pieces of information the same?",
        [SameAs, DifferentThan],
        agent=agent,
    )

    thought, answer = await info_eq(
        F(
            f"""First piece of information: "{text1}"

Second piece of information: "{text2}"
    """
        ).strip()
    )
    if debug:
        print(thought)
        print(answer)
    return answer == SameAs()


@dataclass(frozen=True)
class LessInformative:
    desc: Optional[
        str
    ] = "Choose this option if the first piece is less informative than the second piece."


@dataclass(frozen=True)
class MoreInformative:
    desc: Optional[
        str
    ] = "Choose this option if the first piece is more informative the second piece."


@dataclass(frozen=True)
class Incomparable:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are incomparable."


async def info_cmp(
    text1: str, text2: str, agent: Optional[Agent] = None, debug: bool = False
) -> Union[LessInformative, SameAs, MoreInformative, Incomparable]:
    info_cmp = createCITO(
        """Which of the input pieces of information is more informative?

# Examples

Example:
First piece of information: "8 * 8 = 64 and 64 is the number of squares on a chessboard"
Second piece of information: "8 * 8 = 64"
GreaterThan

Example:
First piece of information: "8 * 8 = 64"
Second piece of information: "8 * 8 = 64 and 64 is the number of squares on a chessboard"
LessThan

Example:
First piece of information: "8 * 8 = 64"
Second piece of information: "The answer is 8 * 8 = 64"
SameAs

Example:
First piece of information: "The sky is blue."
Second piece of information: "The sky is red."
Incomparable
""",
        [LessInformative, SameAs, MoreInformative, Incomparable],
        agent=agent,
    )

    thought, answer = await info_cmp(
        F(
            f"""First piece of information: "{text1}"
Second piece of information: "{text2}"
    """.strip()
        )
    )
    if debug:
        print(thought)
        print(answer)
    return answer
