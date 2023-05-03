import requests
import re
import mwparserfromhell
from dataclasses import dataclass


# Input: location (e.g. "Berlin")
# Output: list of sections of the corresponding Wikivoyage page
# Exceptions: if the location is not found on Wikivoyage, raise an exception
def query_wiki_voyage(location: str):
    url = "https://en.wikivoyage.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "info|revisions",
        "titles": location,
        "inprop": "url",
        "rvprop": "content",  # Get the complete page content
        "rvslots": "*",  # Get all content slots
    }

    response = requests.get(url, params=params)
    data = response.json()
    page = list(data["query"]["pages"].values())[0]
    if "missing" in page:
        raise Exception(f"City '{location}' not found on Wikivoyage.")
    else:
        content = page["revisions"][0]["slots"]["main"]["*"]
        wikicode = mwparserfromhell.parse(content)
        return wikicode.get_sections(flat=True)


# Input: list of sections of a Wikivoyage page
# Output: nested sections, and a list of regions
def parse_sections(sections):
    sections = [parse_section(section) for section in sections]

    # roughly this works by accumulating the root at the beginning of the stack
    # when we exit the current nesting level, we pop back to the right level
    stack = []
    root = {"children": {}}
    stack.append({"level": -1, "node": root})
    regions = []

    for section in sections:
        title = section["title"]
        level = section["level"]
        contents = section["contents"]
        regions += section["regions"]
        node = {"contents": contents, "children": {}}

        # pop back to the right level
        while level <= stack[-1]["level"]:
            stack.pop()

        # add our node to this level
        stack[-1]["node"]["children"][title] = node

        # add our current level to the stack
        stack.append({"level": level, "node": node})

    return root["children"], regions


def stringify_nested_sections(nested_sections) -> str:
    def stringify(node, level):
        contents = node["contents"]
        children = node["children"]
        result = contents
        for title, child in children.items():
            result += "\n" + ("#" * level) + " " + title + "\n"
            result += stringify(child, level + 1)
            result += "\n"
        return result

    return stringify(nested_sections, 1)


@dataclass
class Region:
    name: str
    description: str
    wikilink: str


def parse_region_list(region_list):
    params = region_list.params

    region_names_regex = re.compile(r"region\dname")
    region_descriptions_regex = re.compile(r"region\ddescription")

    region_names_and_urls = [
        (
            param.value.strip_code().strip(),
            param.value.filter_wikilinks()[0].title.strip_code(),
        )
        for param in params
        if region_names_regex.match(param.name.strip_code())
    ]
    print(region_names_and_urls)
    region_descriptions = [
        param.value.strip()
        for param in params
        if region_descriptions_regex.match(param.name.strip_code())
    ]

    return [
        Region(name, description, url)
        for (name, url), description in zip(region_names_and_urls, region_descriptions)
    ]


# takes in a mwparserfromhell section and returns a dict of title, level, and contents
def parse_section(section):
    headings = section.filter_headings()
    # print('templates', section.filter_templates())
    # print('template names', [template.name for template in section.filter_templates()])
    # print('template params', [template.params for template in section.filter_templates()])
    region_lists = section.filter_templates(matches="Regionlist")
    regions = []
    for region_list in region_lists:
        regions += parse_region_list(region_list)
    if headings:
        title = headings[0].title.strip()
        level = headings[0].level
        section.remove(headings[0])
    else:
        title = ""
        level = 0
    contents = section.strip_code().strip()
    # contents = section.strip()
    return {"title": title, "level": level, "contents": contents, "regions": regions}
