from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AnswerDirectly:
    answer: str
    desc: Optional[str] = "Choose this option to provide your answer directly."


@dataclass(frozen=True)
class CannotAnswer:
    reason: str
    desc: Optional[
        str
    ] = "Choose this option if you cannot answer the question. Please explain why."
