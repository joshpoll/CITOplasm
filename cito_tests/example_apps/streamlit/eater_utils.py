# Utils for parsing eater.com
from urllib.parse import urlparse, parse_qs


def parse_place_id(h1, name):
    try:
        services = h1.find_next_sibling("ul", class_="services")
        if services is None:
            raise ValueError(f"No services found for {name}.")

        place_id_link = None
        for link in services.find_all("a"):
            if "google.com/maps/search" in link.get("href", ""):
                place_id_link = link
                break

        if place_id_link is None:
            raise ValueError(f"No Google Maps link found for {name}.")

        url = place_id_link.get("href")
        parsed_url = urlparse(url)
        place_id = parse_qs(parsed_url.query).get("query_place_id", [None])[0]

        # just skip it if the place_id is None
        # if place_id is None:
        #     raise ValueError(f"No place ID found for {name}.")

    except Exception as e:
        raise Exception(f"Error processing {name}: {str(e)}")

    return place_id


def parse_eater_item(h1):
    name = h1.text

    address_div = h1.find_next_sibling(class_="c-mapstack__address-header")
    if address_div is None:
        return None
    address = address_div.select_one("a").text

    description = h1.find_next_sibling(class_="c-entry-content").find("p").text

    place_id = parse_place_id(h1, name)

    if place_id is None:
        return None

    return {
        "name": name,
        "address": address,
        "description": description,
        "place_id": place_id,
    }
