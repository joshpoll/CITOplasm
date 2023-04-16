from dataclasses import dataclass
from typing import Optional, Union

from fvalues import F
from citoplasm.agent.agent import Agent
from citoplasm.cito import Example, createCITO


@dataclass(frozen=True)
class SimilarTo:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are similar."


@dataclass(frozen=True)
class DifferentThan:
    desc: Optional[
        str
    ] = "Choose this option if the two pieces of information are different."


async def info_eq(
    text1: str, text2: str, agent: Optional[Agent] = None, debug: bool = False
) -> bool:
    info_eq = createCITO(
        """Are these two pieces of information similar?""",
        [SimilarTo, DifferentThan],
        examples=[
            Example(
                input='''First piece of information: "3-7"
Second piece of information: "4"''',
                thought="The first piece of information is a range of numbers, and the second piece of information is a number within that range.",
                output=SimilarTo,
            ),
            Example(
                input='''First piece of information: "5"
Second piece of information: "4"''',
                thought="The first piece of information is a number, and the second piece of information is a different number.",
                output=DifferentThan,
            ),
            Example(
                input='''First piece of information: "5.1"
Second piece of information: "4.9"''',
                thought="The first piece of information is a number, and the second piece of information is a different number. However, the two numbers are very close to each other.",
                output=SimilarTo,
            ),
        ],
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
    return answer == SimilarTo()


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
) -> Union[LessInformative, SimilarTo, MoreInformative, Incomparable]:
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
SimilarTo

Example:
First piece of information: "The sky is blue."
Second piece of information: "The sky is red."
Incomparable
""",
        [LessInformative, SimilarTo, MoreInformative, Incomparable],
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
