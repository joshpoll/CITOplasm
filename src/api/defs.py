from dataclasses import dataclass
from typing import List, Optional
from ice.recipe import recipe
from ice.utils import map_async
from src.api.openai_chat_agent import OpenAIChatAgent

from fvalues import F


@dataclass
class Agent:
    name: Optional[str] = None
    desc: str = ""
    model: str = "gpt-3.5-turbo"


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

    if context not in ("", None):
        prompt = F(
            f"""Here is relevant background information:
        
{context}

Answer the following question, using the background information above where helpful. If you do not know the answer, say "I don't know".

Question: "{question}"
Answer: "
"""
        )
    else:
        prompt = F(
            f"""
Answer the following question. If you do not know the answer, say "I don't know".

Question: "{question}"
Answer: "
"""
        )
    return await OpenAIChatAgent().complete(prompt=prompt, stop='"')


def agent_template(agent: Agent, style: Optional[str] = None) -> str:
    if (agent.name is None) or (agent.name == ""):
        return F(f"""{agent.desc} {style or ""}""").strip()
    else:
        return F(f"""You are {agent.name}. {agent.desc} {style or ""}""").strip()


async def chat(
    agent: Agent,
    context: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
    context_template = (
        ""
        if (context is None)
        else F(
            f"""
{context}"""
        )
    )

    prompt = F(
        f"""{agent_template(agent, style=style)}

{context_template}
You: "
"""
    ).strip()
    print(prompt)
    return await OpenAIChatAgent().complete(prompt=prompt, stop='"')


async def explain(agent: Agent, topic: str) -> str:
    return "TODO"


# debate with the user? probably not built in b/c not atomic
# async def debate(agent: Agent, question: str) -> str:
#     return "TODO"


async def classify(text: str, classes: list[str], instructions: str = "") -> str:
    options = F("\n").join(F(f"{i + 1}. {c}") for i, c in enumerate(classes))
    prompt = F(
        f"""{instructions}

{text}

Options:
{options}

Answer with an option number and no other text. eg "2"
"""
    ).strip()
    res = await OpenAIChatAgent().complete(prompt=prompt)
    return classes[int(res) - 1]


# suggest solutions to a problem?
async def suggest(agent: Agent, topic: str) -> str:
    return "TODO"


# list instances of a collection
async def enum(agent: Agent, collection: str, amount: str) -> str:
    prompt = F(
        f"""Provide a list of {amount} {collection}:
-"""
    ).strip()

    return await OpenAIChatAgent().complete(prompt=prompt)


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

    subtopics_text = await OpenAIChatAgent().complete(prompt=prompt)
    subtopics = [line.strip("- ") for line in subtopics_text.split("\n")]
    return subtopics


async def decompose_question(
    question: str, agent: Optional[Agent] = None, amount: str = ""
) -> List[str]:
    prompt = F(
        f"""Break down the following question into {amount} subquestions that can help you understand it better. Make sure each subquestion is self-contained and can be understood without the context of the original question.

Question: {question}
Subquestion:
-"""
    )

    subtopics_text = await OpenAIChatAgent().complete(prompt=prompt)
    subtopics = [line.strip("- ") for line in subtopics_text.split("\n")]
    return subtopics


async_map = map_async
