# type: ignore
from ice.agents.base import Agent
from ice.recipe import recipe

from src.debate.prompt import *


async def turn(debate: Debate, agent: Agent, agent_name: Name, turns_left: int):
    prompt = render_debate_prompt(agent_name, debate, turns_left)
    answer = await agent.complete(prompt=prompt, stop='"')
    return (agent_name, answer.strip('" '))


async def debate(question: str = "Should we legalize all drugs?"):
    agents = [recipe.agent(), recipe.agent()]
    agent_names = ["Alice", "Bob"]
    debate = initialize_debate(question)
    turns_left = 8
    while turns_left > 0:
        for agent, agent_name in zip(agents, agent_names):
            response = await turn(debate, agent, agent_name, turns_left)
            debate.append(response)
            turns_left -= 1

    judgement = await judge(debate)
    debate.append(("Judge", judgement))
    return render_debate(debate)


async def judge(debate: Debate):
    agent = recipe.agent()
    prompt = render_judge_prompt(debate)
    answer = await agent.complete(prompt=prompt, stop='"')
    return answer.strip('" ')


recipe.main(debate)
