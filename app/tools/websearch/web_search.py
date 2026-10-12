import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import requests

from app.tools.websearch.search_intents import match_search_intent

_HTML_SEARCH_URL = "https://html.duckduckgo.com/html/"
_WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
_SESSION = requests.Session()
_HEADERS = {"User-Agent": "JARVIS/1.0"}


class _SearchResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._result: dict[str, str] | None = None
        self._field: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class", "") or ""
        if tag == "div" and "result" in classes.split():
            self._result = {}
        elif tag == "a" and self._result is not None and "result__a" in classes:
            self._result["url"] = _resolve_result_url(attributes.get("href", ""))
            self._field = "title"
            self._parts = []
        elif tag == "a" and self._result is not None and "result__snippet" in classes:
            self._field = "snippet"
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._result is not None and self._field:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._result is not None and self._field:
            self._result[self._field] = " ".join("".join(self._parts).split())
            self._field = None
            self._parts = []
        elif tag == "div" and self._result is not None:
            if self._result.get("title") and self._result.get("url"):
                self.results.append(
                    {
                        "title": self._result["title"],
                        "url": self._result["url"],
                        "snippet": self._result.get("snippet", ""),
                    }
                )
            self._result = None


def has_search_trigger(text: str) -> bool:
    """Return True when a configured web-search intent appears in the message."""
    return match_search_intent(text) is not None


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Return bounded DuckDuckGo HTML search results in one request."""
    if not query or max_results < 1:
        return []
    return _html_search(query, max_results)


def _html_search(query: str, max_results: int) -> list[dict[str, str]]:
    try:
        response = _SESSION.get(
            _HTML_SEARCH_URL,
            params={"q": query},
            headers=_HEADERS,
            timeout=(3, 8),
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    parser = _SearchResultParser()
    parser.feed(response.text)
    return parser.results[:max_results] or _wikipedia_search(query, max_results)


def _wikipedia_search(query: str, max_results: int) -> list[dict[str, str]]:
    try:
        response = _SESSION.get(
            _WIKIPEDIA_SEARCH_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": "1",
                "srlimit": max_results,
            },
            headers=_HEADERS,
            timeout=(3, 8),
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
    except (requests.RequestException, ValueError, TypeError):
        return []

    return [
        {
            "title": str(item["title"]),
            "url": f"https://en.wikipedia.org/?curid={item['pageid']}",
            "snippet": re.sub(r"<[^>]+>", "", str(item.get("snippet", ""))),
        }
        for item in payload.get("query", {}).get("search", [])[:max_results]
        if item.get("title") and item.get("pageid")
    ]


def _resolve_result_url(url: str) -> str:
    if url.startswith("//"):
        url = f"https:{url}"
    query = parse_qs(urlparse(url).query)
    return unquote(query.get("uddg", [url])[0])
