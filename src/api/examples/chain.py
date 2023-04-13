# TODO

# Here's a promising prompt example

# You want to answer the question "What is the log10 of the number of people living in the US vs China?".

# Queries so far:
# - Search(query="Current population of US and China") -> US: 331.9 million and China: 1.412 billion

# You have the opportunity to make more queries. For the next query, choose the option that will most help you give an accurate answer.

# You must pick from one of the following options:
# - AnswerDirectly(answer=str) # You provide your answer directly.
# - Search(query=str) # Search Google for the given query.
# - Python(expr=str) # Run the given expr in a Python REPL.
# - Calculate(expr=str) # Run a calculation using Python syntax.

# First think step by step. Refer to previous queries as needed.
# The last line of your response MUST BE one of the options applied to its arguments and no other text.
# For example: "ExampleOption(arg1='example1', arg2='example2')"
# If the option has no arguments, you can just write the name of the option.
# For example: "ExampleOption"


from typing import List, Type

from src.api.classify import *
from src.api.context import LocalStateList


Question = str


@dataclass(frozen=True)
class FinalAnswer(BaseOption):
    answer: str
    desc: Optional[str] = "Choose this option if you have the final answer."


async def chain(question: Question, tools: List[Type]) -> str:
    res: Any = None
    tools = tools + [FinalAnswer]

    with LocalStateList([], lambda s: f"Action: {s[0]}\nResult: {s[1]}") as context:
        while not isinstance(res, FinalAnswer):
            res = await classify(
                question,
                "Answer the following question as best you can. Do not provide Results. They are provided by the tools.",
                tools,
                context=context,
                omit=["run"],
            )
            if not isinstance(res, FinalAnswer):
                observation = await res.run()
                context.append((res, observation))
        return res.answer
