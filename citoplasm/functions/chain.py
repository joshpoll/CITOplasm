from dataclasses import dataclass
from typing import Any, List, Optional, Type
from citoplasm.actions import AnswerDirectly, CannotAnswer
from citoplasm.cito import ErrorAction, createCITO, pp_action_object


Question = str

CHAIN_INSTRUCTIONS = """Answer the question as best you can. DO NOT provide Results, since they are provided by the tools.
Provide just one action at a time. You will have an opportunity to provide future actions later.
Using the prior actions and results in the context, please provide the next action to help answer the question.
DO NOT REPEAT PREVIOUS ACTIONS WITH THE SAME ARGUMENTS. If possible, provide any additional insights or information that has not been mentioned before.
If the previous action resulted in an error, please provide an action that will help you avoid that error.
When you are done, choose the AnswerDirectly action."""


def terminate(action):
    return isinstance(action, AnswerDirectly) or isinstance(action, CannotAnswer)


async def chain(question: Question, tools: List[Type], debug: bool = False) -> str:
    tools = tools + [AnswerDirectly, CannotAnswer]
    _chain = createCITO(CHAIN_INSTRUCTIONS, tools)
    action: Any = None

    steps = 1

    # with LocalStateList(
    #     [],
    #     lambda s: f"---STEP---\nAction: {pretty_print_option_object(s[1])}\nResult: {s[2].strip()}\nJustification: {s[0]}---END STEP---",
    # ) as context:

    context = (
        "This is a list of actions and results from previous steps in your execution."
    )

    while not terminate(action) and steps <= 5:
        thought, action = await _chain(question, context=context)
        if isinstance(action, ErrorAction):
            # Add a string to the context string containing the thought and the error
            context += "\n" + thought + "\n" + f"{action.err}"
        elif not terminate(action):
            observation = await action.run()
            context += f"\n\n## Step {steps} ##\n# Thought #\n{thought if thought else 'None'}\n\n# Action #\n{pp_action_object(action)}\n\n# Result #\n{observation.strip()}"
        steps += 1
        if debug:
            print(thought)
            print(action)

    return action.answer
