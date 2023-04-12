import ast
import re
from typing import Any, Dict, List, Optional, Type, cast
from attr import dataclass, fields

from fvalues import F

from src.api.openai_chat_agent import OpenAIChatAgent


@dataclass(frozen=True)
class BaseOption:
    pass


@dataclass(frozen=True)
class Other(BaseOption):
    desc = "Choose this option if none of the other options apply."


def pretty_print_option(option: Type) -> str:
    class_name = option.__name__
    field_signatures = [
        f"{field.name}={field.type.__name__}"
        for field in fields(option)
        if field.name != "desc"
    ]
    signature = (
        f"""({", ".join(field_signatures)})""" if len(field_signatures) > 0 else ""
    )
    return f"{class_name}{signature}"


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

    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in tree.body.keywords}
    return data_class_constructor(**kwargs)


async def classify(
    text: str,
    instructions: str,
    action_options: List[Type],
    context: Optional[str] = None,
    # output_options: List[Type],
) -> BaseOption:
    action_options = action_options + [Other]
    # output_options = output_options + [Other]

    # get option descriptions
    action_options_descs = [
        field.default
        for option in action_options
        for field in fields(option)
        if field.name == "desc"
    ]

    # output_options_descs = [
    #     field.default
    #     for option in output_options
    #     for field in fields(option)
    #     if field.name == "desc"
    # ]

    action_options_list = F("\n").join(
        F(
            f"- {pretty_print_option(opt)} # {opt_desc}"
            if opt_desc is not None
            else f"- {pretty_print_option(opt)}"
        )
        for opt, opt_desc in zip(action_options, action_options_descs)
    )

    # output_options_list = F("\n").join(
    #     F(
    #         f"- {pretty_print_option(opt)} # {opt_desc}"
    #         if opt_desc is not None
    #         else f"- {pretty_print_option(opt)}"
    #     )
    #     for opt, opt_desc in zip(output_options, output_options_descs)
    # )

    # First, work this out in a step by step way to be sure we have the right answer.
    # Finally, answer on a new line with one of the options applied to its arguments and no other text.
    # For example: "ExampleOption(arg='example')"
    # If the option has no arguments, you can just write the name of the option.
    # For example: "ExampleOption"

    prompt = F(
        f"""
Use the following format:

Input: The input you must consider.
Context: Context for the input. This is optional.

Thought: You should always think about what to do. Work this out in a step by step way to be sure we take the right action.
Action: The next action to perform. It should be applied to its arguments and no other text.
        For example: "ExampleAction(arg='example')"
        If the option has no arguments, you can just write the name of the action.
        For example: "ExampleAction"

You must pick from one of the following actions:
{action_options_list}

Begin! {instructions}

Input: {text}
Context: {context if context is not None else "<none>"}
"""
    ).strip()
    res = await OpenAIChatAgent().complete(prompt=prompt)
    # split thought and action using a regex
    thought, action = re.split(r"Action:\s*", res)
    # remove "Thought:" from thought
    thought = thought.replace("Thought: ", "")
    print("DEBUG: thought", thought)
    print("DEBUG: action", action)
    try:
        res = parse_option({opt.__name__: opt for opt in action_options}, action)
        return res
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Prompt: {prompt}")
        print(f"Thought: {thought}")
        print(f"Action: {action}")
        raise e
