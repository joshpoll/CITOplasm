from typing import Tuple, List


Name = str
Message = str
Turn = Tuple[Name, Message]
Debate = List[Turn]

my_debate: Debate = [
    ("Alice", "I think we should legalize all drugs."),
    ("Bob", "I'm against."),
    ("Alice", "The war on drugs has been a failure. It's time to try something new."),
]
