from dataclasses import dataclass
from typing import List, Optional
from ice.recipe import recipe
from ice.utils import map_async

from fvalues import F


@dataclass
class Agent:
    name: Optional[str] = None
    desc: Optional[str] = None


async def ask(
    question: str,
    agent: Optional[Agent] = None,
    context: str = "",
    reasoning: str = "",
    style: str = "",
) -> str:
    # Answer the following question, using the background information above where helpful
    #
    # Question: "{question}"
    # Answer:

    if agent is None:
        agent = Agent()

    prompt = F(
        f"""Here is relevant background information:
        
{context}

Answer the following question, using the background information above where helpful.

Question: "{question}"
Answer: 
"""
    )
    return recipe.agent().complete(prompt=prompt, stop='"')


async def respond(
    agent: Agent,
    statement: str,
    context: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
    return "TODO"


async def explain(agent: Agent, topic: str) -> str:
    return "TODO"


# debate with the user? probably not built in b/c not atomic
# async def debate(agent: Agent, question: str) -> str:
#     return "TODO"


async def classify(agent: Agent, prompt: str, choices: tuple) -> int:
    return 0


# suggest solutions to a problem?
async def suggest(agent: Agent, topic: str) -> str:
    return "TODO"


# list instances of a collection
async def enum(agent: Agent, collection: str, amount: str) -> str:
    prompt = F(
        f"""Provide a list of {amount} {collection}:
-"""
    ).strip()

    return recipe.agent().complete(prompt=prompt)


# break down one thing into many smaller things
async def decompose(
    topic: str, agent: Optional[Agent] = None, amount: str = ""
) -> List[str]:
    prompt = F(
        f"""Break down the following topic into {amount} components or subtopics that can help you understand it better. Make sure each component or subtopic is self-contained and can be understood without the context of the original topic.

Topic: {topic}
Components:
-"""
    )

    subtopics_text = recipe.agent().complete(prompt=prompt)
    subtopics = [line.strip("- ") for line in subtopics_text.split("\n")]
    return subtopics


async_map = map_async
