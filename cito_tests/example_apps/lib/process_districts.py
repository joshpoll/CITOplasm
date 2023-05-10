from dataclasses import dataclass
import re

from cito_tests.example_apps.lib.process_sections import flatten_section


@dataclass
class Region:
    name: str
    description: str
    wikilink: str


def flatten(l):
    return [item for sublist in l for item in sublist]


def parse_districts(nested_district_section):
    flattened_district_sections = flatten_section("Districts", nested_district_section)
    region_lists = flatten(
        [
            section["body"].filter_templates(matches="Regionlist")
            for section in flattened_district_sections
        ]
    )
    nested_region_list = [
        parse_region_list(region_list) for region_list in region_lists
    ]
    return flatten(nested_region_list)


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
    region_descriptions = [
        param.value.strip()
        for param in params
        if region_descriptions_regex.match(param.name.strip_code())
    ]

    return [
        Region(name, description, url)
        for (name, url), description in zip(region_names_and_urls, region_descriptions)
    ]
