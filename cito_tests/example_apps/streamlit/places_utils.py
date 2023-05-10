# Utils for Google Places
import os
import requests

import streamlit as st


def get_place_details(place_id, api_key=None):
    if api_key is None:
        api_key = os.environ["GOOGLE_MAPS_API_KEY"]
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        response = response.json()
        if response["status"] == "REQUEST_DENIED":
            raise Exception(response["error_message"])
        elif response["status"] == "INVALID_REQUEST":
            raise Exception(f"Invalid request for place_id {place_id}")
        return response
    else:
        return None


time_of_day_mapping = {
    "early morning": ("05:00", "09:29"),
    "morning": ("09:00", "11:59"),
    "lunchtime": ("12:00", "13:59"),
    "afternoon": ("14:00", "18:29"),
    "early afternoon": ("14:00", "15:59"),
    "late afternoon": ("16:00", "18:29"),
    "evening": ("18:30", "21:59"),
    "night": ("22:00", "04:59"),
}

day_mapping = {
    "Sunday": 0,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
}


def time_to_minutes(time):
    hours, minutes = map(int, time.split(":"))
    return hours * 60 + minutes


def time_number_to_minutes(time):
    hours, minutes = int(time[:2]), int(time[2:])
    return hours * 60 + minutes


def is_business_open(business, day, time_of_day):
    # st.write(business)
    periods = business["result"]["opening_hours"]["periods"]
    day_number = day_mapping[day]
    start_time, end_time = time_of_day_mapping[time_of_day]
    start_minutes = time_to_minutes(start_time)
    end_minutes = time_to_minutes(end_time)

    for period in periods:
        if period["open"]["day"] == day_number:
            open_minutes = time_number_to_minutes(period["open"]["time"])
            close_minutes = time_number_to_minutes(period["close"]["time"])
            if close_minutes < open_minutes:
                # ensure that the closing time is the day after the opening time
                assert period["close"]["day"] == (day_number + 1) % 7
                close_minutes += 24 * 60
                # raise Exception(
                #     f"Closing time is before opening time. Not sure how to handle this case. {business['result']['name']} {periods}"
                # )
            if open_minutes <= start_minutes and close_minutes >= end_minutes:
                return True
    return False


def render_reviews(reviews):
    # Start with a header
    md_string = "#### User Reviews\n"

    # Loop through each review
    for i, review in enumerate(reviews, 1):
        # Add the review number
        # md_string += f"Review {i}:\n"

        # Extract fields from the review
        author_name = review.get("author_name", "")
        rating = review.get("rating", "")
        text = review.get("text", "")
        relative_time_description = review.get("relative_time_description", "")

        # Add the review details to the Markdown string
        md_string += f"{author_name}\n"
        md_string += f"{relative_time_description}\n"
        md_string += f"Rating: {rating} {'stars' if rating != 1 else 'star'}\n"
        md_string += f"{text.strip()}"
        if i != len(reviews):
            md_string += "\n\n---\n\n"  # Add a line separator

    return md_string


def render_business(data):
    # st.write(data)
    # Create markdown string
    markdown = f"### {data['place_details']['result']['name']}\n"

    if "price_level" in data["place_details"]["result"]:
        markdown += (
            f"Price: {'$' * int(data['place_details']['result']['price_level'])}\n"
        )
    else:
        markdown += f"Price: Unknown\n"

    markdown += f"\n#### Description\n{data['description']}\n"

    # limiting to 1 review for now to keep the context small
    markdown += render_reviews(data["place_details"]["result"]["reviews"][:1])

    # st.write(markdown)
    return markdown
