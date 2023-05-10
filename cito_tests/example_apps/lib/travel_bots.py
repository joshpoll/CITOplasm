from citoplasm.cito import createCITO
from typing import List, Optional, Union

from fvalues import F

from citoplasm.agent.agent import Agent
from citoplasm.actions import AnswerDirectly, CannotAnswer
from citoplasm.cito import Example


async def summarize(
    style: Optional[str] = None,
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[AnswerDirectly, CannotAnswer]:
    summarize = createCITO(
        f"""Summarize the information in the context. Be specific and avoid cliches.""".strip(),
        [AnswerDirectly, CannotAnswer],
        agent=agent,
    )

    thought, answer = await summarize(
        style,
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer


async def pick_one(
    input: Optional[str] = None,
    instructions: str = "Pick one of the items in the given list. Only return the name.",
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[AnswerDirectly, CannotAnswer]:
    pick_one = createCITO(
        instructions.strip(),
        [AnswerDirectly, CannotAnswer],
        agent=agent,
    )

    thought, answer = await pick_one(
        input,
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer


async def convert_to_markdown(
    input: Optional[str] = None,
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[AnswerDirectly, CannotAnswer]:
    pick_one = createCITO(
        f"""Convert the input data to markdown.""".strip(),
        [AnswerDirectly, CannotAnswer],
        agent=agent,
    )

    thought, answer = await pick_one(
        input,
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer
