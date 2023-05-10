# Input: list of sections of a Wikivoyage page
# Output: nested sections
def parse_sections(sections):
    sections = [parse_section(section) for section in sections]

    # roughly this works by accumulating the root at the beginning of the stack
    # when we exit the current nesting level, we pop back to the right level
    stack = []
    root = {"sections": {}}
    stack.append({"level": -1, "node": root})

    for section in sections:
        title = section["title"]
        level = section["level"]
        body = section["body"]
        node = {"body": body, "sections": {}}

        # pop back to the right level
        while level <= stack[-1]["level"]:
            stack.pop()

        # add our node to this level
        stack[-1]["node"]["sections"][title] = node

        # add our current level to the stack
        stack.append({"level": level, "node": node})

    return root["sections"][""]


# takes in a mwparserfromhell section and returns a dict of title, level, and body
def parse_section(section):
    headings = section.filter_headings()
    if headings:
        title = headings[0].title.strip()
        level = headings[0].level
        section.remove(headings[0])
    else:
        title = ""
        level = 0
    return {"title": title, "level": level, "body": section}


def flatten_section(title, section):
    flattened = [{"title": title, "body": section["body"]}]
    for title, section in section["sections"].items():
        flattened += flatten_section(title, section)
    return flattened


# inputs a nested section and outputs a string
# the title is preceded by # corresponding to depth starting at 1.
def stringify_nested_section(nested_section, level=1) -> str:
    string = nested_section["body"].strip() + "\n\n"
    for title, section in nested_section["sections"].items():
        string += "#" * level + " " + title + "\n"
        string += stringify_nested_section(section, level + 1)
    return string
