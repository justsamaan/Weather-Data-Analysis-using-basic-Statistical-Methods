"""
weather_api.py
Fetch real-time weather data from the Open-Meteo API (free, no API key).
Returns current conditions and a 7-day hourly DataFrame.
"""

import requests
import pandas as pd
from datetime import datetime
from config import BASE_URL, HOURLY_VARS, FORECAST_DAYS
from location import LocationInfo


def fetch_weather(location: LocationInfo) -> tuple[dict, pd.DataFrame]:
    """
    Fetch forecast data from Open-Meteo.

    Returns
    -------
    current : dict
        Snapshot of current weather conditions extracted from
        the hourly data closest to now.
    df : pd.DataFrame
        Full 7-day hourly DataFrame indexed by datetime.
    """
    params = {
        "latitude":      location.latitude,
        "longitude":     location.longitude,
        "hourly":        ",".join(HOURLY_VARS),
        "forecast_days": FORECAST_DAYS,
        "timezone":      location.timezone,
        "wind_speed_unit": "kmh",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Weather API request failed: {exc}") from exc

    hourly = data.get("hourly", {})
    times  = hourly.get("time", [])
    if not times:
        raise RuntimeError("No hourly data returned from Open-Meteo.")

    # Build DataFrame
    df = pd.DataFrame(hourly)
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")

    # Extract current conditions: row closest to now
    now = pd.Timestamp.now(tz=None)  # naive, same as Open-Meteo timestamps
    deltas = (df.index - now).to_pytimedelta()
    closest_idx = int(min(range(len(deltas)), key=lambda i: abs(deltas[i])))
    current_row = df.iloc[closest_idx]

    current = {
        "timestamp":   df.index[closest_idx].strftime("%Y-%m-%d %H:%M"),
        **{col: round(float(current_row[col]), 2)
           for col in HOURLY_VARS if col in current_row.index},
    }

    return current, df
