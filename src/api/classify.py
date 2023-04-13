import ast
import re
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast
from dataclasses import dataclass, fields

from fvalues import F
from src.api.context import LocalStateList

from src.api.openai_chat_agent import OpenAIChatAgent


def print_with_color(text, color):
    color_codes = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "reset": "0",
    }

    print(f"\033[{color_codes[color]}m{text}\033[0m")


@dataclass(frozen=True)
class BaseOption:
    pass


@dataclass(frozen=True)
class Other(BaseOption):
    desc: str = "Choose this option if none of the other options apply."


@dataclass(frozen=True)
class ErrorAction(BaseOption):
    err: Exception
    desc: str = "Error."


def pretty_print_option(option: Type, omit: Optional[List[str]] = None) -> str:
    omit = omit or []
    omit = omit + ["desc"]

    class_name = option.__name__
    field_signatures = [
        f"{field.name}={field.type.__name__}"
        for field in fields(option)
        if field.name not in omit
    ]
    signature = (
        f"""({", ".join(field_signatures)})""" if len(field_signatures) > 0 else ""
    )
    return f"{class_name}{signature}"


def pretty_print_option_object(obj: Any, omit: Optional[List[str]] = None) -> str:
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


def parse_option(option_map: Dict[str, Type], option: str) -> Any:
    # first strip the option of any whitespace or trailing periods
    option = option.strip().rstrip(".")
    tree = ast.parse(option, mode="eval")
    tree = cast(ast.Expression, tree)

    if isinstance(tree.body, ast.Name):
        constructor = tree.body
        data_class_constructor = option_map.get(constructor.id)

        if data_class_constructor is None:
            raise ValueError(f"Unknown option: {constructor.id}")

        return data_class_constructor()

    if not isinstance(tree.body, ast.Call) or not isinstance(tree.body.func, ast.Name):
        raise ValueError(f"Invalid input: {option}")

    constructor = tree.body.func

    data_class_constructor = option_map[constructor.id]

    if data_class_constructor is None:
        raise ValueError(f"Unknown option: {constructor.id}")

    # special-case the Other option since sometimes the LLM will give it fake arguments
    if data_class_constructor == Other:
        return Other()

    args = [ast.literal_eval(arg) for arg in tree.body.args]
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords}
    return data_class_constructor(*args, **kwargs)


async def classify(
    text: str,
    instructions: str,
    action_options: List[Type],
    context: Union[Optional[str], LocalStateList] = None,
    omit: Optional[List[str]] = None,
    show_thought: bool = False,
) -> Union[BaseOption, Tuple[BaseOption, str]]:
    action_options = action_options + [Other]

    # get option descriptions
    action_options_descs = [
        field.default
        for option in action_options
        for field in fields(option)
        if field.name == "desc"
    ]

    action_options_list = F("\n").join(
        F(
            f"- {pretty_print_option(opt, omit)} # {opt_desc}"
            if opt_desc is not None
            else f"- {pretty_print_option(opt, omit)}"
        )
        for opt, opt_desc in zip(action_options, action_options_descs)
    )

    # First, work this out in a step by step way to be sure we have the right answer.
    # Finally, answer on a new line with one of the options applied to its arguments and no other text.
    # For example: "ExampleOption(arg='example')"
    # If the option has no arguments, you can just write the name of the option.
    # For example: "ExampleOption"

    if isinstance(context, LocalStateList):
        context = str(context)

    prompt = F(
        f"""
---CONTEXT---
{context if context and context is not None else "<none>"}
---END CONTEXT---

---INPUT---
{text}
---END INPUT---

Respond with the following format:

Thought: You should always think about what to do. Work this out in a step by step way to be sure we take the right action. Use the context above to help you make a decision.
Action: The next action to perform when considering the input. YOU MUST APPLY IT TO ITS ARGUMENTS
AND NO OTHER TEXT.
        For example: "ExampleAction(arg='example')"
        If the option has no arguments, you can just write the name of the action.
        For example: "ExampleAction"
        DO NOT WRITE SOMETHING LIKE THIS: "Highlight and copy the population number from the article"

You MUST pick from one of the following actions:
{action_options_list}

Begin! {instructions}
Thought:
"""
    ).strip()
    res = await OpenAIChatAgent().complete(prompt=prompt)
    # split thought and action using a regex
    split_res = re.split(r"Action:\s*", res)
    # thought may not exist
    thought = split_res[0] if len(split_res) > 1 else ""
    action = split_res[-1]

    # remove "Thought:" from thought
    thought = thought.replace("Thought: ", "")
    try:
        # print(f"Prompt: {prompt}")
        # print(f"Thought: {thought}")
        # print(f"Action: {action}")
        res = parse_option({opt.__name__: opt for opt in action_options}, action)
        if show_thought:
            return res, thought
        return res
    except Exception as e:
        print_with_color(f"Error: {e}", "red")
        print_with_color(f"Prompt: {prompt}", "red")
        print_with_color(f"Thought: {thought}", "red")
        print_with_color(f"Action: {action}", "red")
        return ErrorAction(e), thought
        # raise e
