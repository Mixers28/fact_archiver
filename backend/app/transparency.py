from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Artifact, Assessment, SourceItem, TransparencyLogEntry


def _date_key(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def _hash_dict(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _merkle_root(hashes: list[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    level = hashes[:]
    while len(level) > 1:
        next_level: list[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            combined = hashlib.sha256(f"{left}{right}".encode("utf-8")).hexdigest()
            next_level.append(combined)
        level = next_level
    return level[0]


def _source_item_payload(item: SourceItem) -> dict:
    return {
        "id": str(item.id),
        "url": item.url,
        "canonical_url": item.canonical_url,
        "publisher": item.publisher,
        "published_at": item.published_at.isoformat() if item.published_at else None,
        "discovered_at": item.discovered_at.isoformat() if item.discovered_at else None,
        "content_type": item.content_type,
        "language": item.language,
        "capture_tier": item.capture_tier,
        "capture_status": item.capture_status,
        "title": item.title,
    }


def _artifact_payload(artifact: Artifact) -> dict:
    return {
        "id": str(artifact.id),
        "source_item_id": str(artifact.source_item_id),
        "type": artifact.type,
        "storage_uri": artifact.storage_uri,
        "bytes": artifact.bytes,
        "sha256": artifact.sha256,
        "created_at": artifact.created_at.isoformat() if artifact.created_at else None,
        "tool_version": artifact.tool_version,
    }


def _assessment_payload(assessment: Assessment) -> dict:
    return {
        "id": str(assessment.id),
        "claim_id": str(assessment.claim_id),
        "model_version": assessment.model_version,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        "status": assessment.status,
        "score": assessment.score,
        "rationale": assessment.rationale,
        "computed_signals": assessment.computed_signals,
    }


def _hashes_for_items(items: Iterable[SourceItem]) -> list[str]:
    hashes = [_hash_dict(_source_item_payload(item)) for item in items]
    return sorted(hashes)


def _hashes_for_artifacts(artifacts: Iterable[Artifact]) -> list[str]:
    hashes = [_hash_dict(_artifact_payload(artifact)) for artifact in artifacts]
    return sorted(hashes)


def _hashes_for_assessments(assessments: Iterable[Assessment]) -> list[str]:
    hashes = [_hash_dict(_assessment_payload(assessment)) for assessment in assessments]
    return sorted(hashes)


def compute_daily_merkle_root(db: Session, date_key: str) -> str:
    items = (
        db.execute(select(SourceItem).where(SourceItem.discovered_at.isnot(None)))
        .scalars()
        .all()
    )
    items = [item for item in items if _date_key(item.discovered_at) == date_key]
    artifacts = (
        db.execute(select(Artifact).where(Artifact.created_at.isnot(None))).scalars().all()
    )
    artifacts = [artifact for artifact in artifacts if _date_key(artifact.created_at) == date_key]
    assessments = (
        db.execute(select(Assessment).where(Assessment.created_at.isnot(None)))
        .scalars()
        .all()
    )
    assessments = [
        assessment for assessment in assessments if _date_key(assessment.created_at) == date_key
    ]

    leaf_hashes = (
        _hashes_for_items(items)
        + _hashes_for_artifacts(artifacts)
        + _hashes_for_assessments(assessments)
    )
    return _merkle_root(leaf_hashes)


def append_daily_log_entry(db: Session, date_key: str) -> TransparencyLogEntry:
    merkle_root = compute_daily_merkle_root(db, date_key)
    previous = db.execute(
        select(TransparencyLogEntry).order_by(TransparencyLogEntry.created_at.desc())
    ).scalar_one_or_none()
    entry = TransparencyLogEntry(
        previous_root=previous.merkle_root if previous else None,
        merkle_root=merkle_root,
    )
    db.add(entry)
    db.commit()
    return entry
