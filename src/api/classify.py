import ast
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
        f"{field.name}: {field.type.__name__}"
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


async def classify(text: str, instructions: str, options: List[Type]) -> Type:
    options = options + [Other]

    # get option descriptions
    option_descs = [
        field.default
        for option in options
        for field in fields(option)
        if field.name == "desc"
    ]

    options_list = F("\n").join(
        F(
            f"- {pretty_print_option(opt)} # {opt_desc}"
            if opt_desc is not None
            else f"- {pretty_print_option(opt)}"
        )
        for opt, opt_desc in zip(options, option_descs)
    )

    prompt = F(
        f"""{instructions}

{text}

You must pick from one of the following options:
{options_list}

Answer with one of the options applied to its arguments and no other text.
For example: "ExampleOption(arg='example')"
If the option has no arguments, you can just write the name of the option.
For example: "ExampleOption"
"""
    ).strip()
    res = await OpenAIChatAgent().complete(prompt=prompt)
    return parse_option({opt.__name__: opt for opt in options}, res)
