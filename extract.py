import requests
import json
from datetime import datetime

def extract_weather():
    # Open-Meteo's forecast endpoint — free, no API key required
    url = "https://api.open-meteo.com/v1/forecast"

    # Query parameters: location + which hourly fields we want back
    params = {
        "latitude": 40.7128,   # NYC — change to your city's coordinates
        "longitude": -74.0060,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "auto"     # auto-detects timezone based on lat/lon
    }

    # Send the GET request to the API
    response = requests.get(url, params=params)

    # Raises an error immediately if the request failed (e.g. 404, 500)
    # instead of silently continuing with bad/empty data
    response.raise_for_status()

    # Convert the raw response body into a Python dict
    data = response.json()

    # Save the raw JSON to disk, named with today's date.
    # Keeping the raw file is good practice — if transform.py has a bug,
    # you can re-run it on this saved file without hitting the API again.
    with open(f"raw_weather_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(data, f)

    return data

# This block only runs when you execute this file directly
# (not when it's imported by another script, like load.py does)
if __name__ == "__main__":
    extract_weather()