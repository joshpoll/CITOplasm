from dataclasses import dataclass
from typing import Optional

from fvalues import F


@dataclass
class Agent:
    name: Optional[str] = None
    desc: str = ""
    model: str = "gpt-3.5-turbo"


def agent_template(agent: Agent, style: Optional[str] = None) -> str:
    if (agent.name is None) or (agent.name == ""):
        return F(f"""{agent.desc} {style or ""}""").strip()
    else:
        return F(f"""You are {agent.name}. {agent.desc} {style or ""}""").strip()
