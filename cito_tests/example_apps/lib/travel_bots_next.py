from dataclasses import dataclass
from citoplasm.cito import createCITO
from typing import List, Optional, Type, Union

from fvalues import F

from citoplasm.agent.agent import Agent
from citoplasm.actions import AnswerDirectly, CannotAnswer
from citoplasm.cito import Example
from citoplasm.cito_next import create_CITO_next


@dataclass(frozen=True)
class AnswerTitleAsJSON:
    answer: str
    desc: Optional[
        str
    ] = """Choose this option to provide your title as JSON. Respond with a JSON object containing just the title: {"title": "The hottest club in town"}. Do not provide any other text."""


async def summarize(
    input: str,
    style: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[AnswerDirectly, CannotAnswer]:
    thought, answer = await create_CITO_next(
        agent=Agent(
            name="SummarizeBot",
            desc="Summarize the information in the input. Be specific and avoid cliches.",
        ),
        instructions=f"""1. Think about the key points in the input. What are the most important things to know?
2. Summarize the information in the input. Be specific and avoid cliches.

{style}""".strip(),
        context=None,
        output_actions=[AnswerDirectly, CannotAnswer],
        examples=None,
        input=input,
    )
    if debug:
        print(thought)
        print(answer)
    return answer


async def pick_one(
    input: str,
    constraints: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
    answer_format: Type = None,
) -> Union[Type, CannotAnswer]:
    if answer_format is None:
        answer_format = AnswerDirectly

    thought, answer = await create_CITO_next(
        agent=Agent(
            name="PickOneBot",
            desc="Pick one of the items in the input list. Make sure the item satisfies the objectives and constraints provided in the relevant context.",
        ),
        instructions="""1. Think about the objectives and constraints in the context, and how they relate to the items in the input.
2. Pick an item in the input list that satisfies those constraints and maximizes the objectives.""",
        context=constraints,
        output_actions=[
            answer_format,
            CannotAnswer,
        ],
        examples=None,
        input=input,
    )

    if debug:
        print(thought)
        print(answer)
    return answer


async def travel_writer(
    input: str,
    style: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[Type, CannotAnswer]:
    thought, answer = await create_CITO_next(
        agent=Agent(
            name="TravelWriterBot",
            desc="Write a paragraph that might appear in a travel article about the input location. Be specific and avoid cliches.",
        ),
        instructions=f"""1. Think about the key facts about the input location. What are the most important things to know?
2. Write an engaging paragraph that might appear in a travel article about the input location. Be specific and avoid cliches.

{style}""".strip(),
        context=None,
        output_actions=[AnswerDirectly, CannotAnswer],
        examples=None,
        input=input,
    )
    if debug:
        print(thought)
        print(answer)
    return answer


async def travel_writer_titler(
    input: str,
    style: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[Type, CannotAnswer]:
    thought, answer = await create_CITO_next(
        agent=Agent(
            name="TravelWriterBot",
            desc="Write a title for a section of a travel article about the input.",
        ),
        instructions=f"""Here are some examples of titles for sections of travel articles:
If you're writing about a historic diner that celebrates basketball icons, you might title the section "Dine with the legends"
If you're writing about a hot new club, you might title the section "The hottest club in town"

{style}""".strip(),
        context=None,
        output_actions=[AnswerTitleAsJSON, CannotAnswer],
        examples=None,
        input=input,
    )
    if debug:
        print(thought)
        print(answer)
    return answer


# async def convert_to_markdown(
#     input: Optional[str] = None,
#     context: Optional[str] = None,
#     agent: Optional[Agent] = None,
#     debug: bool = False,
# ) -> Union[AnswerDirectly, CannotAnswer]:
#     pick_one = createCITO(
#         f"""Convert the input data to markdown.""".strip(),
#         [AnswerDirectly, CannotAnswer],
#         agent=agent,
#     )

#     thought, answer = await pick_one(
#         input,
#         context=context,
#     )
#     if debug:
#         print(thought)
#         print(answer)
#     return answer
