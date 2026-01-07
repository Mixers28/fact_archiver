import re

_WHITELIST_PHRASES = {
    "public health",
    "central bank",
    "central banks",
    "human rights",
    "civil rights",
    "public safety",
    "national security",
    "foreign policy",
}
_WHITELIST_TOKENS = {
    "politics",
    "government",
    "election",
    "elections",
    "policy",
    "economy",
    "economic",
    "finance",
    "financial",
    "markets",
    "inflation",
    "health",
    "outbreak",
    "outbreaks",
    "security",
    "defense",
    "war",
    "conflict",
    "conflicts",
    "disaster",
    "disasters",
    "courts",
    "court",
    "justice",
    "corruption",
    "environment",
    "climate",
    "energy",
    "infrastructure",
    "science",
    "technology",
    "tech",
    "cyber",
    "regulation",
    "regulatory",
    "sanctions",
    "trade",
    "immigration",
    "refugees",
}
_EXCLUDE_PHRASES = {
    "opinion",
    "editorial",
    "op-ed",
    "entertainment",
    "celebrity",
    "lifestyle",
    "travel",
    "fashion",
    "food",
    "sports",
    "horoscope",
}
_EXCLUDE_TOKENS = {
    "opinion",
    "editorial",
    "opinionated",
    "column",
    "commentary",
    "sports",
    "sport",
    "entertainment",
    "celebrity",
    "lifestyle",
    "travel",
    "fashion",
    "food",
    "horoscope",
    "culture",
}


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _matches_phrases(text: str, phrases: set[str]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def is_significant(categories: list[str], title: str, summary: str) -> bool:
    category_text = " ".join(categories).strip()
    if category_text:
        if _matches_phrases(category_text, _EXCLUDE_PHRASES):
            return False
        category_tokens = _tokenize(category_text)
        if category_tokens & _EXCLUDE_TOKENS:
            return False
        if _matches_phrases(category_text, _WHITELIST_PHRASES):
            return True
        return bool(category_tokens & _WHITELIST_TOKENS)

    fallback_text = " ".join([title, summary]).strip()
    if not fallback_text:
        return False
    if _matches_phrases(fallback_text, _EXCLUDE_PHRASES):
        return False
    fallback_tokens = _tokenize(fallback_text)
    if fallback_tokens & _EXCLUDE_TOKENS:
        return False
    if _matches_phrases(fallback_text, _WHITELIST_PHRASES):
        return True
    return bool(fallback_tokens & _WHITELIST_TOKENS)
