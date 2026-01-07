from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Event, EventMembership, NormalizedText, SourceItem
from app.text_utils import hash_text, normalize_text


def upsert_normalized_text(db: Session, source_item: SourceItem, raw_text: str) -> NormalizedText:
    existing = db.execute(
        select(NormalizedText).where(NormalizedText.source_item_id == source_item.id)
    ).scalar_one_or_none()
    if existing:
        return existing

    normalized = normalize_text(raw_text)
    text_hash = hash_text(normalized)
    canonical = db.execute(
        select(NormalizedText).where(NormalizedText.text_hash == text_hash)
    ).scalar_one_or_none()

    record = NormalizedText(
        source_item_id=source_item.id,
        canonical_source_item_id=canonical.source_item_id if canonical else None,
        text_hash=text_hash,
        normalized_text=normalized,
    )
    db.add(record)
    db.commit()
    return record


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def cluster_source_item(
    db: Session, source_item: SourceItem, threshold: float = 0.6
) -> EventMembership:
    existing = db.execute(
        select(EventMembership).where(EventMembership.source_item_id == source_item.id)
    ).scalar_one_or_none()
    if existing:
        return existing

    date_key = source_item.discovered_at.strftime("%Y-%m-%d")
    candidates = db.execute(select(Event).where(Event.date_key == date_key)).scalars().all()
    best_event = None
    best_score = 0.0
    if source_item.title:
        for event in candidates:
            score = similarity(source_item.title, event.title)
            if score >= threshold and score > best_score:
                best_event = event
                best_score = score

    if best_event is None:
        title = source_item.title or source_item.url
        best_event = Event(title=title, date_key=date_key)
        db.add(best_event)
        db.commit()

    membership = EventMembership(
        event_id=best_event.id, source_item_id=source_item.id, confidence=best_score
    )
    db.add(membership)
    db.commit()
    return membership


def cluster_source_items(db: Session, items: Iterable[SourceItem]) -> int:
    created = 0
    for item in items:
        cluster_source_item(db, item)
        created += 1
    return created


def list_unclustered_items(db: Session) -> list[SourceItem]:
    subquery = select(EventMembership.source_item_id)
    return (
        db.execute(
            select(SourceItem)
            .where(~SourceItem.id.in_(subquery))
            .where(SourceItem.is_filtered.is_(False))
        )
        .scalars()
        .all()
    )


def merge_events(db: Session, source_event_id: str, target_event_id: str) -> None:
    raise NotImplementedError("merge_events is a placeholder for Phase 6 UI wiring.")


def split_event(db: Session, event_id: str, source_item_ids: list[str]) -> None:
    raise NotImplementedError("split_event is a placeholder for Phase 6 UI wiring.")
