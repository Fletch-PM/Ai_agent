import re


def _words(text):
    return set(re.findall(r"\b\w+\b", text.lower()))


def rerank(query, results, limit=5):
    query_words = _words(query)
    query_text = query.lower().strip()

    def score(item):
        text = item.get("parent", item.get("text", "")).lower()
        words = _words(text)
        coverage = len(query_words & words) / max(len(query_words), 1)
        phrase = query_text in text
        return phrase, coverage

    return sorted(results, key=score, reverse=True)[:limit]
