"""Sub-agent intents and examples used by the JARVIS router."""

import re
from dataclasses import dataclass

from app.tools.weather.weather_intents import (
    WEATHER_INTENTS,
    WeatherIntent,
    match_weather_intent,
)
from app.tools.websearch.search_intents import (
    SEARCH_INTENTS,
    SearchIntent,
    match_search_intent,
)


@dataclass(frozen=True)
class SubAgentIntent:
    """Intent metadata that can be extended with additional training examples."""

    name: str
    phrases: tuple[str, ...]
    examples: tuple[str, ...]


AUTHOR_INTENT = SubAgentIntent(
    name="author",
    phrases=(
        "write a paper",
        "research paper",
        "write an essay",
        "draft an article",
        "create a report",
        "compose a paper",
        "generate an essay",
        "make a docx file",
        "create a docs file",
        "save it as a Word document",
    ),
    examples=(
        "Write a research paper about autism.",
        "Can you draft an essay about climate change?",
        "Create a report about our sales performance.",
        "Compose an article about Python.",
        "Make a DOCX file about retrieval augmented generation.",
    ),
)

RAG_INTENT = SubAgentIntent(
    name="rag",
    phrases=(
        "my profile",
        "my resume",
        "my professional background",
        "my experience",
        "my skills",
        "about me",
        "who am I",
        "my reference",
    ),
    examples=(
        "Tell me about my professional background.",
        "What skills do I have?",
        "Who am I?",
        "Use my resume to answer this.",
    ),
)

IDENTITY_INTENT = SubAgentIntent(
    name="identity",
    phrases=("who are you", "what are you", "your name"),
    examples=(
        "Who are you?",
        "What is your name?",
        "What are you?",
    ),
)

SUB_AGENT_INTENTS = (
    IDENTITY_INTENT,
    AUTHOR_INTENT,
    RAG_INTENT,
    *SEARCH_INTENTS,
    *WEATHER_INTENTS,
)
Intent = SubAgentIntent | SearchIntent | WeatherIntent


_AUTHOR_INTENT_PATTERN = re.compile(
    r"\b(?:write|draft|create|compose|generate)\b.*\b(?:paper|essay|article|report)\b"
    r"|\b(?:research\s+paper|term\s+paper)\b"
    r"|\b(?:write|make|create|generate|save)\b.*\b(?:docx?|docs?\s+file|"
    r"word\s+document|word\s+file)\b",
    re.IGNORECASE,
)

_DOCUMENT_OUTPUT_PATTERN = re.compile(
    r"\b(?:docx?|docs?\s+file|document|word\s+(?:document|file))\b",
    re.IGNORECASE,
)
_RAG_INTENT_PATTERN = re.compile(
    r"\b(?:my\s+(?:profile|resume|(?:professional\s+)?background|experience|skills|name|reference)"
    r"|about\s+me|who\s+am\s+i)\b",
    re.IGNORECASE,
)
_IDENTITY_INTENT_PATTERN = re.compile(
    r"\b(?:who\s+are\s+you|what\s+are\s+you|what(?:'s|\s+is)\s+your\s+name)\b",
    re.IGNORECASE,
)


def match_author_intent(text: str) -> SubAgentIntent | None:
    """Return the author intent matched anywhere in the user's request."""
    if _AUTHOR_INTENT_PATTERN.search(text):
        return AUTHOR_INTENT
    return None


def match_rag_intent(text: str) -> SubAgentIntent | None:
    """Return the personal-reference RAG intent matched in the request."""
    if _RAG_INTENT_PATTERN.search(text):
        return RAG_INTENT
    return None


def match_identity_intent(text: str) -> SubAgentIntent | None:
    """Return the identity intent matched in the request."""
    if _IDENTITY_INTENT_PATTERN.search(text):
        return IDENTITY_INTENT
    return None


def match_researcher_intent(text: str) -> SearchIntent | WeatherIntent | None:
    """Return the researcher intent matched anywhere in the user's request."""
    if match_author_intent(text) is not None:
        return None
    return match_search_intent(text) or match_weather_intent(text)


def match_sub_agent_intent(text: str) -> Intent | None:
    """Return the selected sub-agent intent, giving author requests priority."""
    return (
        match_identity_intent(text)
        or match_author_intent(text)
        or match_rag_intent(text)
        or match_researcher_intent(text)
    )


def is_author_request(text: str) -> bool:
    """Return whether the request should be routed to the Author Agent."""
    return match_author_intent(text) is not None


def is_document_request(text: str) -> bool:
    """Return whether the user explicitly requested a document file."""
    return _DOCUMENT_OUTPUT_PATTERN.search(text) is not None


def is_rag_request(text: str) -> bool:
    """Return whether the request asks about the user's personal data."""
    return match_rag_intent(text) is not None


def is_identity_request(text: str) -> bool:
    """Return whether the user is asking about the assistant's identity."""
    return match_identity_intent(text) is not None


def is_researcher_request(text: str) -> bool:
    """Return whether the request explicitly asks for web or weather research."""
    return match_researcher_intent(text) is not None
