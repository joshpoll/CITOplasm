import ast
from dataclasses import dataclass, fields
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypedDict, cast

from fvalues import F

from citoplasm.agent.agent import Agent
from citoplasm.agent.openai_chat_agent import OpenAIChatAgent
from citoplasm.cito import (
    ErrorAction,
    Example,
    Output,
    Thought,
    parse_action,
    pp_action_object,
    pp_actions,
)
from citoplasm.functions.chain import CHAIN_INSTRUCTIONS
from citoplasm.util import print_with_color


@dataclass(frozen=True)
class AnswerAsAgent:
    answer: Type
    desc: str = "Choose this option if you are done simulating the agent. Provide the action that the agent would take next."


# a function that checks whether a given action is an instance of a list of action types
def is_action_instance(action: Type, action_types: List[Type]) -> bool:
    for action_type in action_types:
        if isinstance(action, action_type):
            return True
    return False


async def promptAgent(
    prompt: str, output_actions: List[Type]
) -> Tuple[Thought, Output]:
    res = await OpenAIChatAgent().complete(prompt=prompt)
    # split thought and action using a regex
    # split_res = re.split(r"Action:\s*", res)
    split_res = re.split(r"# Action #\s*", res)
    # thought may not exist
    thought = split_res[0].strip() if len(split_res) > 1 else ""
    action = split_res[-1].strip()

    # remove "# Thought" from thought
    thought = thought.replace("# Thought #", "").strip()
    try:
        # print(f"Prompt: {prompt}")
        # print(f"Thought: {thought}")
        # print(f"Action: {action}")
        parsed_action = parse_action(
            {opt.__name__: opt for opt in output_actions}, action
        )
        # if show_thought:
        #     return res, thought
        return thought, parsed_action
    except Exception as e:
        print_with_color(f"Error: {e}", "red")
        print_with_color(f"Result: {res}", "blue")
        print_with_color(f"Prompt: {prompt}", "red")
        print_with_color(f"Thought: {thought}", "red")
        print_with_color(f"Action: {action}", "red")
        return thought, ErrorAction(e)
        # raise e


def createChain(
    instructions: str,
    tools: List[Type],
    output_actions: List[Type],
    examples: Optional[List[Example]] = None,
    agent: Optional[Agent] = None,
):
    # tools = tools + [AnswerAsAgent]

    formatted_examples = (
        F("\n").join(
            F(
                f"""## Example {i + 1} ##
{example.input}

# Thought #
{example.thought}

# Action #
{pp_action_object(example.output)}
"""
            )
            for i, example in enumerate(examples)
        )
        if examples is not None
        else None
    )

    async def chain(
        input: str, context: Optional[str] = None, debug: bool = False
    ) -> Tuple[Thought, Output]:
        chain_context = "This is a list of actions and results from previous steps in your execution."
        prompt = lambda chain_context: F(
            f"""You are a universal agent simulator. You'll be given some instructions, relevant context, a response format, and possibly some examples. You will use these to inform your own behavior as a simulator. You will then be given a description of an agent to simulate and an input to that agent.
Your goal is to simulate the agent's behavior on the input.

### Instructions ###

Simulate the agent as best you can. DO NOT provide Results, since they are provided by the tools.
Provide just one action at a time. You will have an opportunity to provide future actions later.
Using the prior actions and results in the context, please provide the next action to help simulate the agent.
DO NOT REPEAT PREVIOUS ACTIONS WITH THE SAME ARGUMENTS. If possible, provide any additional insights or information that has not been mentioned before.
If the previous action resulted in an error, please provide an action that will help you avoid that error.
When you are done, answer with one of the agent's actions.

### Relevant Context ###

{chain_context if chain_context and chain_context is not None else "<none>"}

### Response Format ###

Respond with the following format:

# Thought #
You should always think about what to do. Work this out in a step by step way to be sure we take the right action. Use the context above to help you make a decision.

# Action #
The next action to perform when considering the input.

Output the name of an action and some arguments. For example: "ExampleAction(arg='example')"

Do not output any text other than the action and its arguments.
For example, DO NOT WRITE: "Highlight and copy the population number from the article"
Another example, DO NOT WRITE: "Result: ExampleAction(arg='example')"

If the option has no arguments, you can just write the name of the action. For example: "ExampleAction"

You MUST pick from one of the following actions:
{pp_actions(tools)}

### Agent Description ###

{instructions}

## Relevant Context ##

{context if context and context is not None else "<none>"}

## Available Actions ##

You MUST pick from one of the following actions:
{pp_actions(output_actions)}

{f'''## Examples ##

Here are some examples of valid responses given an input and the instructions and context above:

{formatted_examples}
''' if examples is not None else ""}

Begin!

## Input ##

{input}
"""
        ).strip()
        # print_with_color(f"PROMPT {prompt}", "blue")

        action: Any = None
        steps = 1
        max_steps = 3

        while not is_action_instance(action, output_actions) and steps <= max_steps:
            thought, action = await promptAgent(
                prompt(chain_context), tools + output_actions
            )
            if isinstance(action, ErrorAction):
                chain_context += "\n" + thought + "\n" + f"{action.err}"
            elif not is_action_instance(action, output_actions):
                observation = await action.run()
                chain_context += f"\n\n## Step {steps} ##\n# Thought #\n{thought if thought else 'None'}\n\n# Action #\n{pp_action_object(action)}\n\n# Result #\n{observation.strip()}"
            steps += 1
            if debug:
                print_with_color(f"Step {steps - 1}", "blue")
                print_with_color(f"Thought: {thought}", "blue")
                print_with_color(f"Action: {action}", "blue")
                print_with_color(f"Result: {observation}", "blue")
                # print_with_color(f"Context: {chain_context}", "blue")
                print_with_color(f"Prompt: {prompt(chain_context)}", "blue")
                # print_with_color(f"Steps: {steps}", "blue")
                # print_with_color(f"Max Steps: {max_steps}", "blue")
                # print_with_color(f"Action: {action}", "blue")

        # return thought, action.answer
        return thought, action

    return chain
