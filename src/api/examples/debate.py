from typing import List
from fvalues import F
from src.api.defs import *

Name = str
Message = str
Turn = tuple[Name, Message]
Debate = List[Turn]


def render_debate(debate: Debate, self_name: Optional[Name] = None) -> str:
    debate_text = ""
    for speaker, text in debate:
        if speaker == self_name:
            speaker = "You"
        debate_text += F(f'{speaker}: "{text}"\n')
    return debate_text.strip()


async def get_participants() -> List[Agent]:
    alice = Agent(
        name="Alice",
        desc="You are trying to win the debate using reason and evidence. Take a position and defend it.",
    )
    bob = Agent(
        name="Bob",
        desc="You are trying to win the debate using reason and evidence. Take a position not taken by Alice and defend it.",
    )
    return [alice, bob]


async def debate(question: str) -> str:
    debate = [("Question", question)]
    participants = await get_participants()

    turns_left = 8
    while turns_left > 0:
        for participant in participants:
            response = await respond(
                participant,
                "",
                context=F(
                    f"""There are {turns_left} turns left in the debate.

{render_debate(debate, participant.name)}
"""
                ).strip(),
                style="Don't repeat yourself. No more than 1-2 sentences.",
            )
            debate.append((participant.name or "", response))
            turns_left -= 1
    return render_debate(debate)


# example prompt:
"""
You are Alice. You are trying to win the debate using reason and evidence. Take a position and
defend it.

Here's the context:
There are 8 turns left in the debate.

Question: "Should we legalize all drugs?"
You: I'm for it.
Bob: I'm against it.
You: I think it would be good for the economy.
Bob: I think it would be bad for the economy.

Respond. Don't repeat yourself. No more than 1-2 sentences.
You:
"""
