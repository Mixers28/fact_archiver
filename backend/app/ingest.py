from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable

import feedparser

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SourceItem
from app.significance import is_significant


@dataclass
class IngestResult:
    created: int
    skipped: int


def _load_lines(path: str) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    lines: list[str] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None


def _source_item_exists(db: Session, url: str) -> bool:
    stmt = select(SourceItem.id).where(SourceItem.url == url)
    return db.execute(stmt).scalar_one_or_none() is not None


def ingest_urls(db: Session, urls: Iterable[str]) -> IngestResult:
    created = 0
    skipped = 0
    for url in urls:
        if _source_item_exists(db, url):
            skipped += 1
            continue
        db.add(
            SourceItem(
                url=url,
                canonical_url=url,
                discovered_at=datetime.utcnow(),
                capture_tier=1,
                capture_status="pending",
                is_significant=True,
                is_filtered=False,
            )
        )
        created += 1
    db.commit()
    return IngestResult(created=created, skipped=skipped)


def ingest_urls_from_file(db: Session, path: str) -> IngestResult:
    return ingest_urls(db, _load_lines(path))


def ingest_rss(db: Session, feed_urls: Iterable[str]) -> IngestResult:
    created = 0
    skipped = 0
    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        publisher = getattr(feed.feed, "title", None)
        for entry in feed.entries:
            url = getattr(entry, "link", None)
            if not url:
                continue
            categories = [
                str(tag.get("term", "")).strip()
                for tag in getattr(entry, "tags", []) or []
                if isinstance(tag, dict)
            ]
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
            if not is_significant(categories, title, summary):
                skipped += 1
                continue
            if _source_item_exists(db, url):
                skipped += 1
                continue
            published_at = _parse_datetime(getattr(entry, "published", None))
            db.add(
                SourceItem(
                    url=url,
                    canonical_url=url,
                    title=getattr(entry, "title", None),
                    publisher=publisher,
                    published_at=published_at,
                    discovered_at=datetime.utcnow(),
                    capture_tier=1,
                    capture_status="pending",
                    is_significant=True,
                    is_filtered=False,
                )
            )
            created += 1
    db.commit()
    return IngestResult(created=created, skipped=skipped)


def ingest_rss_from_file(db: Session, path: str) -> IngestResult:
    return ingest_rss(db, _load_lines(path))
