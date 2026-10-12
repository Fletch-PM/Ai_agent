"""Weather-intent vocabulary and location extraction used by JARVIS."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherIntent:
    name: str
    phrases: tuple[str, ...]
    examples: tuple[str, ...]


WEATHER_INTENTS = (
    WeatherIntent(
        name="weather_lookup",
        phrases=(
            "weather",
            "forecast",
            "temperature",
            "is it raining",
            "will it rain",
            "rain today",
        ),
        examples=(
            "Search the weather in Quezon City.",
            "Look up the forecast for Manila tomorrow.",
            "Can you check the temperature in London?",
            "Search if it will rain in Cebu today.",
        ),
    ),
)

_WEATHER_INTENT_PATTERN = re.compile(
    r"\b(?:weather|forecast|temperature|is\s+it\s+raining|will\s+it\s+rain|rain\s+today)\b",
    re.IGNORECASE,
)
_LOCATION_PATTERN = re.compile(r"\b(?:in|on|for|at)\s+(.+?)(?:\?|$)", re.IGNORECASE)


def match_weather_intent(text: str) -> WeatherIntent | None:
    """Return the configured weather intent matched anywhere in the text."""
    if _WEATHER_INTENT_PATTERN.search(text):
        return WEATHER_INTENTS[0]
    return None


def extract_weather_location(text: str) -> str:
    """Extract a likely place from a natural weather request."""
    match = _LOCATION_PATTERN.search(text)
    if match:
        return match.group(1).strip(" ?,. ")

    location = _WEATHER_INTENT_PATTERN.sub(" ", text, count=1)
    location = re.sub(
        r"\b(what's|what|is|today|now|currently|please|can|you|check|search|look|up)\b",
        " ",
        location,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", location).strip(" ?,. ")
