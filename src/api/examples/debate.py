from typing import List
from fvalues import F
from src.api.defs import *

Name = str
Message = str
Turn = tuple[Name, Message]
Debate = List[Turn]


def render_debate(
    question: str, positions: Debate, debate: Debate, self_name: Optional[Name] = None
) -> str:
    debate_text = F(f'Question: "{question}"\n')
    debate_text += "\n"
    if positions:
        debate_text += "Positions:\n"
        for speaker, text in positions:
            if speaker == self_name:
                speaker = "You"
            debate_text += F(f'{speaker}: "{text}"\n')
        debate_text += "\n"
    if debate:
        debate_text += "Debate:\n"
        for speaker, text in debate:
            if speaker == self_name:
                speaker = "You"
            debate_text += F(f'{speaker}: "{text}"\n')
    return debate_text.strip()


async def get_participants() -> List[Agent]:
    alice = Agent(
        name="Alice",
        desc="You are a seasoned debater, trying to win the debate using reason and evidence. State your position IN ONE SENTENCE.",
    )
    bob = Agent(
        name="Bob",
        desc="You are a seasoned debater, trying to win the debate using reason and evidence. State your position IN ONE SENTENCE. I must be different than Alice's.",
    )
    return [alice, bob]


async def debate(question: str) -> str:
    positions: Debate = [
        # ("Alice", "I'm in favor."),
        # ("Bob", "I'm against."),
    ]
    debate: Debate = []
    participants = await get_participants()
    turns_left = 8

    # initialize debate
    for participant in participants:
        response = await chat(
            participant,
            context=F(
                f"""
    {render_debate(question, positions, debate, participant.name)}
    """
            ).strip(),
        )
        positions.append((participant.name or "", response))
        participant.desc = f"""You are trying to win the debate using reason and evidence. There \
    are {turns_left} turns left in the debate. Don't repeat yourself. IMPORTANT: Use only
1-2 sentences per turn."""

    while turns_left > 0:
        for i, participant in enumerate(participants):
            response = await chat(
                participant,
                context=F(
                    f"""
{render_debate(question, positions, debate, participant.name)}
"""
                ).strip(),
            )
            debate.append((participant.name or "", response))
            turns_left -= 1
            participant.desc = f"""You are a seasoned debater, trying to win the debate using reason and evidence. There \
are {turns_left} turns left in the debate. Be specific. Don't repeat yourself. IMPORTANT: Use only
1-2 sentences per turn."""
    return render_debate(question, positions, debate)
