from datetime import datetime


def render_restaurant(data):
    # Create markdown string
    markdown = f"### {data['name']}\n"
    markdown += f"- type: {data['type']}\n"
    markdown += f"- website: {data['website']}\n"
    markdown += f"- rating: {data['rating']}\n"
    markdown += f"- review count: {data['review_count']}\n"
    markdown += f"- price: {data['price']}\n"

    markdown += f"\n#### Description\n{data['description']}\n"

    markdown += "\n#### User Reviews\n"
    for review in data["user_reviews"]:
        markdown += f"- {review['user']['name']}: {review['summary']}\n"

    # Format hours
    # markdown += "\n#### Hours\n"
    # for day, hours in data["hours"].items():
    #     markdown += f"- {day.capitalize()}: "
    #     markdown += (
    #         "Closed\n"
    #         if hours["opens"] == "Closed"
    #         else f"{hours['opens']} - {hours['closes']}\n"
    #     )

    return markdown


#     "early morning": ("05:00", "08:59"),
#     "morning": ("09:00", "11:59"),
#     "lunchtime": ("12:00", "13:59"),
#     "afternoon": ("14:00", "17:59"),
#     "early afternoon": ("14:00", "15:59"),
#     "late afternoon": ("16:00", "17:59"),
#     "evening": ("18:00", "21:59"),
#     "night": ("22:00", "04:59")


def is_restaurant_open(restaurant_data, day, time_of_day):
    time_of_day_mapping = {
        "early morning": ("05:00 AM", "09:29 AM"),
        "morning": ("09:00 AM", "11:59 AM"),
        "lunchtime": ("12:00 PM", "01:59 PM"),
        "afternoon": ("02:00 PM", "06:29 PM"),
        "early afternoon": ("02:00 PM", "03:59 PM"),
        "late afternoon": ("04:00 PM", "06:29 PM"),
        "evening": ("06:30 PM", "09:59 PM"),
        "night": ("10:00 PM", "04:59 AM"),
    }

    data = restaurant_data
    hours = data["hours"].get(day.lower())

    if hours is None or hours["opens"] == "Closed" or hours["closes"] == "Closed":
        return False

    opening_parts = hours["opens"].split("\u202f")
    closing_parts = hours["closes"].split("\u202f")

    if len(opening_parts) == 2:
        opening_time_str, opening_am_pm = opening_parts
    else:
        opening_time_str = opening_parts[0]
        opening_am_pm = closing_parts[1]  # infer AM/PM from "closes"

    closing_time_str, closing_am_pm = closing_parts

    # Add ":00" if necessary
    opening_time_str = (
        opening_time_str if ":" in opening_time_str else opening_time_str + ":00"
    )
    closing_time_str = (
        closing_time_str if ":" in closing_time_str else closing_time_str + ":00"
    )

    opening_time_str += " " + opening_am_pm
    closing_time_str += " " + closing_am_pm

    opening_time = datetime.strptime(opening_time_str, "%I:%M %p").time()
    closing_time = datetime.strptime(closing_time_str, "%I:%M %p").time()

    start_time, end_time = time_of_day_mapping[time_of_day]

    start_time = datetime.strptime(start_time, "%I:%M %p").time()
    end_time = datetime.strptime(end_time, "%I:%M %p").time()

    if closing_time > opening_time:
        return (
            opening_time <= start_time <= closing_time
            or opening_time <= end_time <= closing_time
        )
    else:
        return not (
            closing_time <= start_time <= opening_time
            or closing_time <= end_time <= opening_time
        )
