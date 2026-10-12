from functools import lru_cache
from typing import Any
from urllib.parse import urlencode

import requests

from app.tools.weather.weather_intents import extract_weather_location, match_weather_intent

_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_SESSION = requests.Session()
_HEADERS = {"User-Agent": "JARVIS/1.0"}


def is_weather_query(query: str) -> bool:
    return match_weather_intent(query) is not None


def weather_search(query: str) -> list[dict[str, str]]:
    location_query = extract_weather_location(query)
    if not location_query:
        return []

    location = _geocode(location_query)
    if not location:
        return []

    try:
        response = _SESSION.get(
            _FORECAST_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "forecast_days": 1,
                "timezone": "auto",
            },
            headers=_HEADERS,
            timeout=(3, 8),
        )
        response.raise_for_status()
        forecast: dict[str, Any] = response.json()
        current = forecast["current"]
        daily = forecast["daily"]
        place = ", ".join(
            part
            for part in (location.get("name"), location.get("admin1"), location.get("country"))
            if part
        )
    except (KeyError, IndexError, TypeError, requests.RequestException, ValueError):
        return []

    summary = (
        f"Current conditions in {place}: {current['temperature_2m']}°C, "
        f"feels like {current['apparent_temperature']}°C, humidity "
        f"{current['relative_humidity_2m']}%, wind {current['wind_speed_10m']} km/h. "
        f"Today's range is {daily['temperature_2m_min'][0]}°C to "
        f"{daily['temperature_2m_max'][0]}°C, with a "
        f"{daily['precipitation_probability_max'][0]}% precipitation chance."
    )
    forecast_url = f"{_FORECAST_URL}?{urlencode({'latitude': location['latitude'], 'longitude': location['longitude'], 'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m', 'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max', 'forecast_days': 1, 'timezone': 'auto'})}"
    return [{"title": f"Live weather for {place}", "url": forecast_url, "snippet": summary}]


@lru_cache(maxsize=64)
def _geocode(location_query: str) -> dict[str, Any] | None:
    try:
        response = _SESSION.get(
            _GEOCODING_URL,
            params={"name": location_query, "count": 1, "language": "en", "format": "json"},
            headers=_HEADERS,
            timeout=(3, 8),
        )
        response.raise_for_status()
        return (response.json().get("results") or [None])[0]
    except (AttributeError, IndexError, TypeError, requests.RequestException, ValueError):
        return None
