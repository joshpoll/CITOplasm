import ast
from dataclasses import dataclass, fields
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, cast

from fvalues import F

from citoplasm.agent.agent import Agent
from citoplasm.agent.openai_chat_agent import OpenAIChatAgent
from citoplasm.util import print_with_color


@dataclass(frozen=True)
class Other:
    desc: str = "Choose this option if none of the other options apply."


@dataclass(frozen=True)
class ErrorAction:
    err: Exception
    desc: str = "Error."


def parse_action(action_map: Dict[str, Type], action: str) -> Any:
    # first strip the option of any whitespace or trailing periods
    action = action.strip().rstrip(".")
    tree = ast.parse(action, mode="eval")
    tree = cast(ast.Expression, tree)

    if isinstance(tree.body, ast.Name):
        constructor = tree.body
        data_class_constructor = action_map.get(constructor.id)

        if data_class_constructor is None:
            raise ValueError(f"Unknown option: {constructor.id}")

        return data_class_constructor()

    if not isinstance(tree.body, ast.Call) or not isinstance(tree.body.func, ast.Name):
        raise ValueError(f"Invalid input: {action}")

    constructor = tree.body.func

    data_class_constructor = action_map[constructor.id]

    if data_class_constructor is None:
        raise ValueError(f"Unknown option: {constructor.id}")

    # special-case the Other option since sometimes the LLM will give it fake arguments
    if data_class_constructor == Other:
        return Other()

    args = [ast.literal_eval(arg) for arg in tree.body.args]
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords}
    return data_class_constructor(*args, **kwargs)


def pp_action(action: Type) -> str:
    omit = ["desc"]

    class_name = action.__name__
    field_signatures = [
        f"{field.name}={field.type.__name__}"
        for field in fields(action)
        if field.name not in omit
    ]
    signature = (
        f"""({", ".join(field_signatures)})""" if len(field_signatures) > 0 else ""
    )
    return f"{class_name}{signature}"


def pp_action_object(obj: Any, omit: Optional[List[str]] = None) -> str:
    omit = omit or []
    omit = omit + ["desc"]

    class_name = obj.__class__.__name__
    field_values = [
        f"{field.name}={repr(getattr(obj, field.name))}"
        for field in fields(obj)
        if field.name not in omit
    ]
    values = f"""({", ".join(field_values)})""" if len(field_values) > 0 else ""
    return f"{class_name}{values}"


def pp_actions(actions: List[Type]) -> str:
    # actions = actions + [Other]

    # get option descriptions
    action_descs = [
        field.default
        for option in actions
        for field in fields(option)
        if field.name == "desc"
    ]

    actions_string = F("\n").join(
        F(
            f"- {pp_action(action)} # {action_desc}"
            if action_desc is not None
            else f"- {pp_action(action)}"
        )
        for action, action_desc in zip(actions, action_descs)
    )

    return actions_string


Thought = str
Output = Any


# CITO: (context, input) -> (thought, output)
# returns a CITO function
def createCITO(
    instructions: str, output_actions: List[Type], agent: Optional[Agent] = None
):
    async def cito(input: str, context: Optional[str] = None) -> Tuple[Thought, Output]:
        prompt = F(
            f"""You are a CITO agent. You'll be given some contextual information, some instructions for this step, and some input data.

Respond with the following format:

# Thought
You should always think about what to do. Work this out in a step by step way to be sure we take the right action. Use the context above to help you make a decision.

# Action
The next action to perform when considering the input.

Output the name of an action and some arguments. For example: "ExampleAction(arg='example')"

Do not output any text other than the action and its arguments.
For example, DO NOT WRITE: "Highlight and copy the population number from the article"
Another example, DO NOT WRITE: "Result: ExampleAction(arg='example')"

If the option has no arguments, you can just write the name of the action. For example: "ExampleAction"

You MUST pick from one of the following actions:
{pp_actions(output_actions)}

Begin!

---

# Instructions

{instructions}

# Relevant Context

{context if context and context is not None else "<none>"}

# Input

{input}


"""
        ).strip()
        # print_with_color(f"PROMPT {prompt}", "blue")

        res = await OpenAIChatAgent().complete(prompt=prompt)
        # split thought and action using a regex
        # split_res = re.split(r"Action:\s*", res)
        split_res = re.split(r"# Action\s*", res)
        # thought may not exist
        thought = split_res[0].strip() if len(split_res) > 1 else ""
        action = split_res[-1].strip()

        # remove "# Thought" from thought
        thought = thought.replace("# Thought", "").strip()
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

    return cito
