import asyncio
from dataclasses import dataclass
import os
import sys
from typing import Optional
from bs4 import BeautifulSoup
import json

import requests

sys.path.append(os.getcwd())

from cito_tests.example_apps.streamlit.eater_utils import parse_eater_item
from cito_tests.example_apps.streamlit.places_utils import (
    get_place_details,
    is_business_open,
    render_business,
)
from cito_tests.example_apps.streamlit.see import render_sight
from citoplasm.actions import AnswerDirectly

from citoplasm.tools.search import search_json


import streamlit as st

from cito_tests.example_apps.lib.process_sections import stringify_nested_section
from cito_tests.example_apps.lib.travel_bots_next import (
    pick_one,
    summarize,
    travel_writer,
    travel_writer_titler,
)
import cito_tests.example_apps.lib.travel_new as travel

# Where to Stay - tripadvisor?
# How to Get There - google maps?


st.header("36 hours in X")
st.text_input("Where do you want to go?", key="location")


async def get_wiki_voyage_data(location: str):
    sections = travel.query_wiki_voyage(location)
    parsed_sections, extra_data = travel.parse_document(sections)
    summary = await summarize(
        stringify_nested_section(parsed_sections["Understand"])[:10000],
        style="Provide your answer as though it were the introduction to a travel article. Highlight a couple of unique characteristics about the location.",
    )
    return summary, extra_data


summary = None
extra_data = None
if "location" in st.session_state and st.session_state.location:
    summary, extra_data = asyncio.run(get_wiki_voyage_data(st.session_state.location))

if summary:
    st.write(summary["Thought"])

# loosely based on some of the NYT 36 Hours articles I read
# activity_template = [
#     {"day": "Friday", "time": "in the afternoon", "activity": "See"},
#     {"day": "Friday", "time": "at lunchtime", "activity": "Eat"},
#     {"day": "Friday", "time": "at night", "activity": "Drink"},
#     {"day": "Saturday", "time": "in the morning", "activity": "Eat"},
#     {"day": "Saturday", "time": "in the morning", "activity": "Do"},
#     {"day": "Saturday", "time": "at lunchtime", "activity": "Eat"},
#     {"day": "Saturday", "time": "in the early afternoon", "activity": "See"},
#     {"day": "Saturday", "time": "in the late afternoon", "activity": "Do"},
#     {"day": "Saturday", "time": "in the evening", "activity": "Eat"},
#     {"day": "Saturday", "time": "at night", "activity": "Drink"},
#     {"day": "Sunday", "time": "in the early morning", "activity": "Do"},
#     {"day": "Sunday", "time": "in the morning", "activity": "Eat"},
#     {"day": "Sunday", "time": "at lunchtime", "activity": "Eat"},
#     {"day": "Sunday", "time": "at lunchtime", "activity": "Buy"},
# ]
activity_template = [
    {"day": "Friday", "time": "afternoon", "activity": "See"},
    {"day": "Friday", "time": "lunchtime", "activity": "Eat"},
    {"day": "Friday", "time": "night", "activity": "Drink"},
    {"day": "Saturday", "time": "morning", "activity": "Eat"},
    {"day": "Saturday", "time": "morning", "activity": "Do"},
    {"day": "Saturday", "time": "lunchtime", "activity": "Eat"},
    {"day": "Saturday", "time": "early afternoon", "activity": "See"},
    {"day": "Saturday", "time": "late afternoon", "activity": "Do"},
    {"day": "Saturday", "time": "evening", "activity": "Eat"},
    {"day": "Saturday", "time": "night", "activity": "Drink"},
    {"day": "Sunday", "time": "early morning", "activity": "Do"},
    {"day": "Sunday", "time": "morning", "activity": "Eat"},
    {"day": "Sunday", "time": "lunchtime", "activity": "Eat"},
    {"day": "Sunday", "time": "lunchtime", "activity": "Buy"},
]


async def get_top_sights(location: str):
    if location == "Seattle" and os.path.exists("seattle_top_sights.json"):
        with open("seattle_top_sights.json") as f:
            return json.load(f)
    search_results = await search_json(f"Top sights in {location}")
    top_sights = search_results["top_sights"]["sights"]
    if location == "Seattle" and not os.path.exists("seattle_top_sights.json"):
        with open("seattle_top_sights.json", "w") as f:
            json.dump(top_sights, f)
    return top_sights


async def get_eater_restaurants(location: str):
    search_results = await search_json(f"{location} restaurants site:eater.com")
    # st.write(search_results)
    url = search_results["organic_results"][0]["link"]
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "html.parser")

    restaurants = []
    for h1 in soup.find_all("h1"):
        res = parse_eater_item(h1)
        if res is not None:
            restaurants.append(res)
    return restaurants


async def get_eater_bars(location: str):
    search_results = await search_json(f"{location} bars site:eater.com")
    # st.write(search_results)
    url = search_results["organic_results"][0]["link"]
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, "html.parser")

    bars = []
    for h1 in soup.find_all("h1"):
        res = parse_eater_item(h1)
        if res is not None:
            bars.append(res)
    return bars


eat_info = None
if "location" in st.session_state and st.session_state.location:
    if st.session_state.location == "Seattle" and os.path.exists(
        "seattle_restaurants.json"
    ):
        eat_info = json.load(open("seattle_restaurants.json"))
    else:
        with st.spinner("Finding restaurants..."):
            eater_restaurants = asyncio.run(
                get_eater_restaurants(st.session_state.location)
            )
            # eat_info = asyncio.run(get_restaurant_data(eater_restaurants))
            # eat_info = [
            #     get_place_details(restaurant["place_id"])
            #     for restaurant in eater_restaurants
            # ]
            eat_info = {
                restaurant["name"]: {
                    "place_details": get_place_details(restaurant["place_id"]),
                    "description": restaurant["description"],
                }
                for restaurant in eater_restaurants
            }
            if st.session_state.location == "Seattle":
                json.dump(eat_info, open("seattle_restaurants.json", "w"))
    # st.write(eat_info)

drink_info = None
if "location" in st.session_state and st.session_state.location:
    if st.session_state.location == "Seattle" and os.path.exists("seattle_bars.json"):
        drink_info = json.load(open("seattle_bars.json"))
    else:
        with st.spinner("Finding bars..."):
            eater_bars = asyncio.run(get_eater_bars(st.session_state.location))
            # drink_info = asyncio.run(get_bar_data(eater_bars))
            # drink_info = [get_place_details(bar["place_id"]) for bar in eater_bars]
            drink_info = {
                bar["name"]: {
                    "place_details": get_place_details(bar["place_id"]),
                    "description": bar["description"],
                }
                for bar in eater_bars
            }
            if st.session_state.location == "Seattle":
                json.dump(drink_info, open("seattle_bars.json", "w"))
    # st.write(drink_info)

sights_info = None
if "location" in st.session_state and st.session_state.location:
    sights_info = asyncio.run(get_top_sights(st.session_state.location))

from ice.utils import map_async


@dataclass(frozen=True)
class AnswerAsJSON:
    answer: str
    desc: Optional[
        str
    ] = """Choose this option to provide your answer as JSON. Respond with a JSON object containing just the name of the item like this: {"name": "The Space Needle"}. Do not provide any other text."""


async def fill_activity_slot(activity_slot, sights_info, eat_info, drink_info):
    day = activity_slot["day"]
    time = activity_slot["time"]
    activity = activity_slot["activity"]
    if activity == "See":
        input_text = "\n\n".join(
            [
                render_sight(sight)
                for sight in sights_info
                # if is_sight_open(sight, day, time)
            ][:10]
        )
        # input_text = stringify_nested_section(district_sections[activity])
        response = await pick_one(
            input_text,
            """Objective: Find a great place to sightsee such as a significant landmark or a nice museum.
Constraints: None.""",
            answer_format=AnswerAsJSON,
        )
    elif activity == "Eat":
        # TODO: this should not recommend the same restaurant twice
        input_text = "\n\n".join(
            [
                render_business(info)
                for _, info in eat_info.items()
                if is_business_open(info["place_details"], day, time)
            ][:10]
        )
        response = await pick_one(
            input_text,
            """Objective: Find a great restaurant.
Constraints: None.""",
            answer_format=AnswerAsJSON,
        )
        # st.write(input_text)
    elif activity == "Drink":
        # TODO: this should not recommend the same bar twice
        # input_text = json.dumps(drink_info)
        input_text = "\n\n".join(
            [
                render_business(info)
                for _, info in drink_info.items()
                # if is_restaurant_open(bar, day, time)
                if is_business_open(info["place_details"], day, time)
            ][:10]
        )
        response = await pick_one(
            input_text,
            """Objective: Find a great bar.
Constraints: None.""",
            answer_format=AnswerAsJSON,
        )
    elif activity == "Do":
        # TODO: add events to this
        input_text = "\n\n".join(
            [
                render_sight(sight)
                for sight in sights_info
                # if is_sight_open(sight, day, time)
            ][:10]
        )
        # input_text = stringify_nested_section(district_sections[activity])
        response = await pick_one(
            input_text,
            """Objective: Find a great thing to do such as going to a park or another tourist attraction that involves physical activity or social interaction.
Constraints: None.""",
            answer_format=AnswerAsJSON,
        )
    elif activity == "Buy":
        # TODO: maybe just search for souvenir shops and marketplaces?
        input_text = "\n\n".join(
            [
                render_sight(sight)
                for sight in sights_info
                # if is_sight_open(sight, day, time)
            ][:10]
        )
        # st.write(input_text)
        # input_text = stringify_nested_section(district_sections[activity])
        response = await pick_one(
            input_text,
            """Objective: Find a great place to buy things after a trip, like a famous store or market.
Constraints: None.""",
            answer_format=AnswerAsJSON,
        )
    else:
        raise ValueError(f"Unknown activity {activity}")
        # input_text = stringify_nested_section(district_sections[activity])
        # input_text = input_text[:10000]
        # response = await pick_one(
        #     input_text,
        #     "There are no constraints."
        #     # f'If you find an item that satisfies the constraints, use the AnswerDirectly response format and respond with a JSON object with the name of the item like this: {{"name": "The Space Needle"}}',
        # )
    # st.write(response)

    thought = response["Thought"]
    try:
        if "AnswerAsJSON" in response:
            extracted_response = json.loads(response["AnswerAsJSON"])["name"]
            # filter out the response from the list of sights, restaurants, bars, etc.
            sights_info = [
                sight for sight in sights_info if sight["title"] != extracted_response
            ]
            # eat_info = [
            #     restaurant
            #     for restaurant in eat_info
            #     if restaurant["name"] != extracted_response
            # ]
            eat_info.pop(extracted_response, None)
            # drink_info = [
            #     bar for bar in drink_info if bar["name"] != extracted_response
            # ]
            drink_info.pop(extracted_response, None)
        else:
            extracted_response = response

    except Exception as e:
        st.write(e)
        extracted_response = response["AnswerAsJSON"]

    return (
        {
            "day": day,
            "time": time,
            "activity": activity,
            "response": extracted_response,
            "thought": thought,
        },
        sights_info,
        eat_info,
        drink_info,
    )


if extra_data:
    itinerary_progress = st.progress(
        1 / (len(activity_template) + 1), "Planning your trip..."
    )
    filled_activity_template = []
    current_sights = sights_info.copy()
    current_eat = eat_info.copy()
    current_drink = drink_info.copy()
    for i, activity in enumerate(activity_template):
        # st.write(activity["activity"])
        filled_activity, current_sights, current_eat, current_drink = asyncio.run(
            fill_activity_slot(activity, current_sights, current_eat, current_drink)
        )
        filled_activity_template.append(filled_activity)
        itinerary_progress.progress(
            (i + 1) / (len(activity_template) + 1), "Planning your trip..."
        )
    itinerary_progress.progress(1.0, "Done planning your trip!")

    # make an h1 for each day
    # make an h2 for each time

    itinerary_progress = st.progress(
        1 / (len(activity_template) + 1), "Writing your itinerary..."
    )
    current_day = None
    for i, activity in enumerate(filled_activity_template):
        if activity["day"] != current_day:
            st.header(activity["day"])
            current_day = activity["day"]
        # look up the activity in the info lists to get some more info
        activity_info = None
        if activity["activity"] == "Eat":
            # TODO: use the other information in the restaurant object
            try:
                activity_info = eat_info[activity["response"]]["description"]
            except KeyError:
                st.write(
                    f"Couldn't find {activity['response']} in {eat_info.keys()}. Skipping..."
                )
        elif activity["activity"] == "Drink":
            try:
                activity_info = drink_info[activity["response"]]["description"]
            except KeyError:
                st.write(
                    f"Couldn't find {activity['response']} in {drink_info.keys()}. Skipping..."
                )
        # elif activity["activity"] == "Do":
        #     activity_info = [
        #         sight for sight in sights_info if sight["title"] == activity["response"]
        #     ][0]

        if activity_info:
            response = asyncio.run(
                travel_writer(
                    f"""### {activity["response"]}
{activity_info}""".strip(),
                )
            )
        else:
            response = asyncio.run(
                travel_writer(
                    f"""{activity["response"]}""".strip(),
                )
            )

        if "AnswerDirectly" in response:
            text = response["AnswerDirectly"]
        else:
            text = str(response)

        response = asyncio.run(travel_writer_titler(text))
        if "AnswerTitleAsJSON" in response:
            title = f'{activity["time"].title()} | {json.loads(response["AnswerTitleAsJSON"])["title"]}'
        else:
            title = f'{activity["time"].title()} | {activity["activity"]}'
        st.subheader(title)
        st.write(text)
        itinerary_progress.progress(
            (i + 1) / (len(activity_template) + 1), "Writing your itinerary..."
        )
    itinerary_progress.progress(1.0, "Done writing your itinerary!")
