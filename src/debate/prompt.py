from fvalues import F

from src.debate.utils import *


def render_debate_prompt(agent_name: str, debate: Debate, turns_left: int) -> str:
    prompt = F(
        f"""
You are {agent_name}. There are {turns_left} turns left in the debate. You are trying to win the debate using reason and evidence. Don't repeat yourself. No more than 1-2 sentences per turn.

{render_debate(debate, agent_name)}
You: "
"""
    ).strip()
    return prompt


def render_judge_prompt(debate: Debate) -> str:
    prompt = F(
        f"""
You are the judge. You are judging the outcome of a debate. Give your opinion on the debate, and
justify it. No more than 1-2 sentences.

{render_debate(debate, None)}
You: "
"""
    ).strip()
    return prompt
