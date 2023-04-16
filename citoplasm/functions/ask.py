from dataclasses import dataclass
from typing import Optional
from citoplasm.actions import AnswerDirectly, CannotAnswer

from citoplasm.agent.agent import Agent
from citoplasm.cito import createCITO


async def ask(
    question: str,
    context: Optional[str] = None,
    agent: Optional[Agent] = None,
    debug: bool = False,
) -> str:
    ask = createCITO(
        "Answer the question as best you can.",
        [AnswerDirectly, CannotAnswer],
        agent=agent,
    )
    thought, answer = await ask(question, context=context)
    if debug:
        print(thought)
        print(answer)
    if isinstance(answer, AnswerDirectly):
        return answer.answer
    else:
        return "I don't know."
