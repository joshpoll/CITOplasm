from dataclasses import dataclass
from typing import List, Optional, Union

from fvalues import F
from citoplasm.actions import AnswerDirectly, CannotAnswer

from citoplasm.agent.agent import Agent
from citoplasm.cito import Example, createCITO


async def distill(
    items: List[str],
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[AnswerDirectly, CannotAnswer]:
    distill = createCITO(
        f"""Identify commonalities between the inputs to distill the list of items to a single item. Make your answer as specific as possible while remaining concise.""".strip(),
        [AnswerDirectly, CannotAnswer],
        examples=[
            Example(
                input="""10 - 10 = 0

2 - 2 = 0

3 - 3 = 0""",
                thought="""I see that all of the inputs are of the form "x - x = 0".""",
                output=AnswerDirectly("x - x = 0"),
            ),
            Example(
                input="""Amy likes apples and bananas.

Bob likes grapes, oranges, and apples.

Charlie likes apples and oranges.""",
                thought='''I see that all of the inputs are of the form "x likes apples and y."''',
                output=AnswerDirectly("x likes apples and y"),
            ),
        ],
        agent=agent,
    )

    formatted_items = F("\n").join(items)

    thought, answer = await distill(
        f"""{formatted_items}""",
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer
