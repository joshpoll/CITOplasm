# Input: location (e.g. "Berlin")
# Output: list of sections of the corresponding Wikivoyage page
# Exceptions: if the location is not found on Wikivoyage, raise an exception
import requests
import mwparserfromhell

from cito_tests.example_apps.lib.process_districts import parse_districts
from cito_tests.example_apps.lib.process_sections import (
    parse_sections,
    stringify_nested_section,
)


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


def parse_document(sections):
    parsed_sections = parse_sections(sections)
    sections = parsed_sections["sections"]

    districts = None
    if "Districts" in sections:
        districts = parse_districts(sections["Districts"])
        print(districts)

    understand = None
    if "Understand" in sections:
        understand = stringify_nested_section(sections["Understand"])
        print(understand)

    return sections, {"districts": districts, "understand": understand}


# TODO: for now we'll focus on Eat, Drink, Do, See, and Buy
