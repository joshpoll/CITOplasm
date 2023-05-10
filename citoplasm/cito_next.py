# CITO: (context, input) -> (thought, output)
# returns a CITO function
# TODO: make examples input better
from dataclasses import fields
import re
from typing import List, Optional, Tuple, Type

from fvalues import F

from citoplasm.agent.agent import Agent, agent_template
from citoplasm.agent.openai_chat_agent import OpenAIChatAgent
from citoplasm.cito import Example, Output, Thought
from citoplasm.util import print_with_color


# INPUT:
# Synopsis(desc="Write the synopsis of the play using the title and your thoughts.")
# OUTPUT:
# ## Synopsis
# (Write the synopsis of the play using the title and your thoughts.)
def render_output_action_template(output_action: Type) -> str:
    # output_action_fields = [
    #     field.default
    #     for field in output_action.__dataclass_fields__.values()
    #     if field.name != "desc"
    # ]

    print(fields(output_action))
    # desc_field = fields(output_action)[0]
    # filter the fields for desc
    desc_field = [field for field in fields(output_action) if field.name == "desc"][0]

    output_action_desc = desc_field.default

    # output_action_fields_string = F("\n").join(
    #     F(f"- {field}") for field in output_action_fields
    # )

    return F(
        f"""## {output_action.__name__}
({output_action_desc if output_action_desc is not None else ""})
""".strip()
    )


def parse_sections(input_string):
    sections = re.split(r"##\s*", input_string)
    sections_dict = {}

    for section in sections:
        if section.strip() == "":
            continue

        title, *body = section.split("\n", 1)
        body = "\n".join(body).strip()
        sections_dict[title] = body

    return sections_dict


async def create_CITO_next(
    agent: Optional[Agent],
    instructions: str,
    context: Optional[str],
    output_actions: List[Type],
    examples: Optional[List[Example]],
    input: str,
):
    if agent is not None:
        agent_prompt = agent_template(agent)
    else:
        agent_prompt = "You are a CITO agent. You'll be given some contextual information, some instructions for this step, and some input data."

    output_actions_string = F("\n\nOr\n\n").join(
        render_output_action_template(output_action) for output_action in output_actions
    )

    prompt = F(
        f"""{agent_prompt}

# Instructions
{instructions}

# Relevant Context
{context if context and context is not None else "None"}

# Response Format
Your response should have two parts: a Thought and an Action.

First think about what to do, and respond in this format:
## Thought
(Briefly describe your thought process. Let's work this out step by step to be sure we take the right action. Use the context above to help you make a decision.)

Then respond with one of the following action formats:
{output_actions_string}


Begin!

# Input
{input}""".strip()
    )

    print_with_color(f"PROMPT {prompt}", "blue")

    res = await OpenAIChatAgent().complete(prompt=prompt)
    sections = parse_sections(res)
    # return a tuple of the Thought section and the rest of the sections
    return sections["Thought"], sections

    # # split thought and action using a regex
    # # split_res = re.split(r"Action:\s*", res)
    # split_res = re.split(r"# Action #\s*", res)
    # # thought may not exist
    # thought = split_res[0].strip() if len(split_res) > 1 else ""
    # action = split_res[-1].strip()

    # # remove "# Thought" from thought
    # thought = thought.replace("# Thought #", "").strip()
    # try:
    #     # print(f"Prompt: {prompt}")
    #     # print(f"Thought: {thought}")
    #     # print(f"Action: {action}")
    #     parsed_action = parse_action(
    #         {opt.__name__: opt for opt in output_actions}, action
    #     )
    #     # if show_thought:
    #     #     return res, thought
    #     return thought, parsed_action
    # except Exception as e:
    #     print_with_color(f"Error: {e}", "red")
    #     print_with_color(f"Result: {res}", "blue")
    #     print_with_color(f"Prompt: {prompt}", "red")
    #     print_with_color(f"Thought: {thought}", "red")
    #     print_with_color(f"Action: {action}", "red")
    #     return thought, ErrorAction(e)
    #     # raise e
