import requests
import re
import mwparserfromhell
from dataclasses import dataclass

from cito_tests.example_apps.lib.process_districts import parse_region_list

# TODO: extract region parsing into a separate function from section parsing
# TODO: make a separate parser for each of the possible top-level sections including these from Cap Hill page: ['Understand', 'Get in', 'See', 'Do', 'Buy', 'Eat', 'Drink', 'Sleep', 'Stay safe', 'Connect']
#       (there's a template page somewhere that lists expected sections)
# TODO: for now we'll focus on Eat, Drink, Do, See, and Buy

# from AutoGPT:
"""
I want Auto-GPT to: Create a "36 hours in Seattle" article in the style of the New York Times.
SeattleGuideGPT  has been created with the following details:
Name:  SeattleGuideGPT
Role:  an AI travel writer that specializes in creating engaging and informative travel guides for various destinations around the world. SeattleGuideGPT is designed to help travelers make the most of their time in Seattle by providing personalized recommendations and insider tips.
Goals:
-  Create a comprehensive and engaging "36 hours in Seattle" article that captures the essence of the city and highlights its top attractions, restaurants, and activities.
-  Provide personalized recommendations based on the traveler's interests, preferences, and budget to ensure a unique and memorable experience.
-  Incorporate insider tips and local knowledge to give readers a deeper understanding of Seattle's culture, history, and lifestyle.
-  Use a writing style that is consistent with the New York Times' brand and tone, while also adding a personal touch to make the article more relatable and engaging.
-  Optimize the article for search engines and social media to increase its visibility and reach among potential readers.
"""


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
