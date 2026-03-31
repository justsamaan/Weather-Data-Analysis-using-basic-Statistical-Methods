"""
location.py
Auto-detect the user's geographic location using IP geolocation (ip-api.com).
No API key required. Free tier allows 45 req/min.
"""

from dataclasses import dataclass
import requests
from config import GEO_URL


@dataclass
class LocationInfo:
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    ip: str


def get_location() -> LocationInfo:
    """
    Query ip-api.com for the caller's approximate location.
    Returns a LocationInfo dataclass.
    Raises RuntimeError if the request fails.
    """
    try:
        response = requests.get(GEO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"ip-api.com returned status '{data.get('status')}': "
                f"{data.get('message', 'unknown error')}"
            )

        return LocationInfo(
            city=data.get("city", "Unknown"),
            region=data.get("regionName", "Unknown"),
            country=data.get("country", "Unknown"),
            latitude=float(data["lat"]),
            longitude=float(data["lon"]),
            timezone=data.get("timezone", "UTC"),
            ip=data.get("query", "N/A"),
        )

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Location detection failed: {exc}") from exc
