from dataclasses import dataclass
from typing import List, Optional, Union
from citoplasm.actions import CannotAnswer

from citoplasm.agent.agent import Agent
from citoplasm.cito import createCITO


@dataclass(frozen=True)
class ItemList:
    items: List[str]
    desc: Optional[str] = "Choose this option to provide a list of items."


async def decompose(
    amount: Union[int, str],
    topic: str,
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> Union[ItemList, CannotAnswer]:
    ask = createCITO(
        f"""Break down the input `topic` into a list of `amount` components or subtopics. Make sure each component or subtopic is self-contained and can be understood without the context of the original topic. You may need information from the context to produce the list.""".strip(),
        [ItemList, CannotAnswer],
        examples=[
            (
                """topic: What is the effect of creatine on cognition?
amount: 2-5""",
                """I need to break down the topic "What is the effect of creatine on cognition?" into between 2 and 5 components or subtopics that can help me understand it better.
# The question seems to be composed of 'creatine', 'cognition', and the relationship between them.""",
                ItemList(
                    items=[
                        "What is creatine?",
                        "What is cognition?",
                        "How does creatine affect cognition?",
                        "What are the benefits of creatine on cognition?",
                        "What are the side effects of creatine on cognition?",
                    ]
                ),
            ),
            (
                """topic: problem solving
amount: 4""",
                """I need to break down the topic "problem solving" into 4 facets.""",
                ItemList(items=["problem", "solution", "algorithm", "heuristic"]),
            ),
        ],
        agent=agent,
    )
    thought, answer = await ask(
        f"""
topic: {topic}
amount: {amount}
""",
        context=context,
    )
    if debug:
        print(thought)
        print(answer)
    return answer
