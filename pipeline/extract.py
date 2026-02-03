"""Extract script to scrape USGS data feed for earthquake data"""

import json
import bs4 as bs
import requests


URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.quakeml"


def check_for_text(event, *tags, default=None):
    """Checks whether the tag contains text, return none if not"""
    current = event
    for tag in tags:
        if current is None:
            return default
        current = current.find(tag)
    return current.text if current else default

def extract_data():
    """Extracts specific information from each event"""
    url_link = requests.get(URL, timeout=10)
    soup = bs.BeautifulSoup(url_link.text, features="xml")
    events = soup.find_all('event')
    data = []
    for e in events:
        event = {}
        event["start_time"] = check_for_text(e, "time", "value")
        event["description"] = check_for_text(e, "description", "text")
        event["creation_time"] = check_for_text(e, "creationInfo", "creationTime")
        event["latitude"] = check_for_text(e, "latitude", "value")
        event["longitude"] = check_for_text(e, "longitude", "value")
        event["depth_value"] = check_for_text(e, "depth", "value")
        event["depth_uncertainty"] = check_for_text(e, "depth", "uncertainty")
        event["used_phase_count"] = check_for_text(e, "quality", "usedPhaseCount")
        event["used_station_count"] = check_for_text(e, "quality", "usedStationCount")
        event["azimuthal_gap"] = check_for_text(e, "quality", "azimuthalGap")
        event["magnitude_value"] = check_for_text(e, "mag", "value")
        event["magnitude_uncertainty"] = check_for_text(e, "mag", "uncertainty")
        event["magnitude_type_name"] = check_for_text(e, "magnitude", "type")
        event["agency_name"] = check_for_text(e, "creationInfo", "agencyID")
        data.append(event)

    return data


def save_data(data):
    """Saves the extracted information to a json file as a list of dictionaries"""
    with open("data/earthquakes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    event_data = extract_data()
    save_data(event_data)
