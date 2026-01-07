from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Assessment, Claim, ClaimAssertion, SourceItem


def compute_signals(db: Session, claim_id: str) -> dict:
    publishers = (
        db.execute(
            select(SourceItem.publisher)
            .join(ClaimAssertion, ClaimAssertion.source_item_id == SourceItem.id)
            .where(ClaimAssertion.claim_id == claim_id)
        )
        .scalars()
        .all()
    )
    independent_sources = len({p for p in publishers if p})
    contradiction_count = (
        db.execute(
            select(func.count())
            .select_from(ClaimAssertion)
            .where(ClaimAssertion.claim_id == claim_id, ClaimAssertion.polarity == "denies")
        )
        .scalar_one()
    )

    return {
        "independent_sources_count": independent_sources,
        "contradiction_count": contradiction_count,
        "primary_evidence_present": False,
        "correction_or_retraction_seen": False,
    }


def status_from_signals(signals: dict) -> tuple[str, float]:
    if signals["contradiction_count"] >= 1:
        return "Contested", 0.3
    if signals["independent_sources_count"] >= 2 and not signals["primary_evidence_present"]:
        return "Corroborated", 0.7
    return "Unverified", 0.2


def rationale_from_signals(signals: dict) -> list[str]:
    bullets: list[str] = []
    bullets.append(f"Independent sources: {signals['independent_sources_count']}")
    if signals["contradiction_count"] >= 1:
        bullets.append(f"Contradictions: {signals['contradiction_count']}")
    if not signals["primary_evidence_present"]:
        bullets.append("No primary evidence detected")
    return bullets


def create_assessment_if_missing(db: Session, claim: Claim) -> Assessment | None:
    existing = db.execute(select(Assessment).where(Assessment.claim_id == claim.id)).scalar_one_or_none()
    if existing:
        return None
    signals = compute_signals(db, str(claim.id))
    status, score = status_from_signals(signals)
    assessment = Assessment(
        claim_id=claim.id,
        model_version="v1",
        status=status,
        score=score,
        rationale=rationale_from_signals(signals),
        computed_signals=signals,
    )
    db.add(assessment)
    db.commit()
    return assessment
