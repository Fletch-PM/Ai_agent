"""Search-intent vocabulary and examples used by JARVIS."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchIntent:
    name: str
    phrases: tuple[str, ...]
    examples: tuple[str, ...]


SEARCH_INTENTS = (
    SearchIntent(
        name="web_search",
        phrases=(
            "search",
            "search web",
            "search the web",
            "look up",
            "browse",
            "find online",
        ),
        examples=(
            "Can you search web for Batman?",
            "Please look up the weather in Quezon City.",
            "Browse the latest technology news.",
            "Find online information about Python.",
        ),
    ),
)

_SEARCH_INTENT_PATTERN = re.compile(
    r"\b(?:search(?:\s+the)?\s+web|search|look\s+up|browse|find\s+online)\b",
    re.IGNORECASE,
)


def match_search_intent(text: str) -> SearchIntent | None:
    """Return the configured intent matched anywhere in the user's text."""
    if _SEARCH_INTENT_PATTERN.search(text):
        return SEARCH_INTENTS[0]
    return None


def extract_search_query(text: str) -> str:
    """Remove the first configured search phrase and conversational filler."""
    query = _SEARCH_INTENT_PATTERN.sub("", text, count=1)
    query = re.sub(
        r"^\s*(?:please|can you|could you|would you|jarvis)\s*[:,]?\s*",
        "",
        query,
        flags=re.IGNORECASE,
    )
    query = re.sub(r"^\s*(?:the\s+web|for|about)\s+", "", query, flags=re.IGNORECASE)
    return query.strip(" :,-?!")
