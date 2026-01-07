from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from app.text_utils import normalize_text

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_QUOTE_RE = re.compile(r"\"([^\"]{3,})\"")
_NUMERIC_RE = re.compile(r"\d")


@dataclass(frozen=True)
class ExtractedClaim:
    normalized_text: str
    claim_type: str
    excerpt: str


def _split_sentences(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(stripped) if s.strip()]


def _unique_claims(claims: Iterable[ExtractedClaim]) -> list[ExtractedClaim]:
    seen: set[tuple[str, str]] = set()
    unique: list[ExtractedClaim] = []
    for claim in claims:
        key = (claim.normalized_text, claim.claim_type)
        if key in seen:
            continue
        seen.add(key)
        unique.append(claim)
    return unique


def extract_claims(text: str) -> list[ExtractedClaim]:
    sentences = _split_sentences(text)
    claims: list[ExtractedClaim] = []

    if sentences:
        headline = normalize_text(sentences[0])
        if headline:
            claims.append(ExtractedClaim(headline, "what", sentences[0]))
        for lead in sentences[1:3]:
            normalized = normalize_text(lead)
            if normalized:
                claims.append(ExtractedClaim(normalized, "what", lead))

    for sentence in sentences:
        if _NUMERIC_RE.search(sentence):
            normalized = normalize_text(sentence)
            if normalized:
                claims.append(ExtractedClaim(normalized, "number", sentence))

    for match in _QUOTE_RE.finditer(text):
        quote = match.group(1).strip()
        normalized = normalize_text(quote)
        if normalized:
            claims.append(ExtractedClaim(normalized, "quote", quote))

    return _unique_claims(claims)
