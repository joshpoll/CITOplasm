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
from test.test_classify import Python


Question = str


@dataclass(frozen=True)
class AnswerDirectly(BaseOption):
    answer: str
    desc: Optional[str] = "Choose this option to provide your answer directly."


async def chain(question: Question, tools: List[Type]) -> str:
    res: Any = None
    tools = tools + [AnswerDirectly]

    fuel = 10

    with LocalStateList(
        [],
        lambda s: f"---STEP---\nAction: {pretty_print_option_object(s[1])}\nResult: {s[2].strip()}\nJustification: {s[0]}---END STEP---",
    ) as context:
        while not isinstance(res, AnswerDirectly) and fuel > 0:
            res, thought = await classify(
                question,
                """Answer the question as best you can. DO NOT provide Results, since they are provided by the tools.
Provide just one action at a time. You will have an opportunity to provide future actions later.
Using the provided actions and results, please provide the next action to help answer the question.
DO NOT REPEAT PREVIOUS ACTIONS WITH THE SAME ARGUMENTS. If possible, provide any additional insights or information that has not been mentioned before.
If the previous action resulted in an error, please provide an action that will help you avoid that error.
When you are done, choose the AnswerDirectly action.""",
                tools,
                context=context,
                show_thought=True,
            )  # type: ignore
            if isinstance(res, ErrorAction):
                # TODO: we shouldn't need to lose the triplet format here...
                context.append((thought, res, ""))
                raise res.err
            elif not isinstance(res, AnswerDirectly):
                observation = await res.run()
                context.append((thought, res, observation))
            fuel -= 1
        print(context)
        return res.answer
