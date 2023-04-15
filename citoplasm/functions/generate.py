from dataclasses import dataclass
from typing import List, Optional, Union

from citoplasm.agent.agent import Agent
from citoplasm.cito import createCITO


@dataclass(frozen=True)
class ItemList:
    items: List[str]
    desc: Optional[str] = "Choose this option to provide a list of items."


@dataclass(frozen=True)
class CannotAnswer:
    reason: str
    desc: Optional[
        str
    ] = "Choose this option if you cannot answer the question. Please provide a reason."


async def generate(
    amount: Union[int, str],
    collection: str,
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[ItemList, CannotAnswer]:
    ask = createCITO(
        f"""List `amount` items in the input `collection`. You may need information from the context to produce the list.

# Examples

Example:
amount: 3
collection: dog names

# Thought
I need to list 3 items in the collection "dog names".
# Action
ItemList(items=["Fido", "Spot", "Rover"])

Example:
amount: 2-5
collection: colors

# Thought
I need to list between 2 and 5 items in the collection "colors".
# Action
ItemList(items=["red", "blue", "green", "yellow"])

Example:
amount: 50
collection: numbers between 1 and 5

# Thought
I need to list 50 items in the collection "numbers between 1 and 5", but there are not 50 numbers between 1 and 5.
# Action
CannotAnswer(reason="There are not 50 numbers between 1 and 5.")

Example:
amount: 10
collection: unique words with three consecutive double letters

# Thought
I need to list 10 items in the collection "unique words with three consecutive double letters." The words I can think of are "bookkeeper", "bookkeeping", and "bookkeepers".
But I can't think of any more.
# Action
CannotAnswer(reason="I can only think of 3 words.")
""".strip(),
        [ItemList, CannotAnswer],
        agent=agent,
    )
    thought, answer = await ask(
        f"""
amount: {amount}
collection: {collection}
""",
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer
