import pandas as pd
import json

def transform_weather(raw_data):
    # The API nests all the time-series data under the "hourly" key
    hourly = raw_data["hourly"]

    # Build a DataFrame from the raw lists — each key becomes a column,
    # and pandas lines them up by position (same index = same hour)
    df = pd.DataFrame({
        "timestamp": hourly["time"],
        "temperature_c": hourly["temperature_2m"],
        "humidity_pct": hourly["relative_humidity_2m"],
        "precipitation_mm": hourly["precipitation"]
    })

    # Convert timestamp strings (e.g. "2026-09-09T00:00") into real
    # datetime objects — needed for sorting, filtering, and plotting later
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Drop any rows with missing values (e.g. a sensor gap in the API data)
    # so bad/incomplete rows don't break downstream steps or the load
    df = df.dropna()

    # Add a derived column — this is a "transform" in the ETL sense:
    # we're not just cleaning, we're creating new value from raw data
    df["temperature_f"] = df["temperature_c"] * 9/5 + 32

    return df

# Only runs when you execute this file directly, not when it's imported
if __name__ == "__main__":
    # Open the raw JSON file saved by extract.py
    # NOTE: you must replace "YOURDATE" with today's actual date,
    # matching whatever extract.py named the file (e.g. raw_weather_20260909.json)
    with open("raw_weather_20260909.json") as f:
        raw = json.load(f)

    df = transform_weather(raw)

    # Quick sanity checks — first 5 rows, and total row count
    print(df.head())
    print(f"Rows: {len(df)}")