import argparse

from sqlalchemy import select

from app.claim_extraction import extract_claims
from app.db import SessionLocal, init_engine
from app.models import Claim, ClaimAssertion, EventMembership, NormalizedText, SourceItem
from app.scoring import create_assessment_if_missing


def _ensure_claim(db, event_id, normalized_text, claim_type):
    existing = db.execute(
        select(Claim).where(
            Claim.event_id == event_id,
            Claim.normalized_text == normalized_text,
            Claim.claim_type == claim_type,
        )
    ).scalar_one_or_none()
    if existing:
        return existing

    claim = Claim(event_id=event_id, normalized_text=normalized_text, claim_type=claim_type)
    db.add(claim)
    db.commit()
    return claim


def _ensure_assertion(db, claim_id, source_item_id, excerpt):
    existing = db.execute(
        select(ClaimAssertion).where(
            ClaimAssertion.claim_id == claim_id,
            ClaimAssertion.source_item_id == source_item_id,
        )
    ).scalar_one_or_none()
    if existing:
        return existing
    assertion = ClaimAssertion(
        claim_id=claim_id,
        source_item_id=source_item_id,
        excerpt=excerpt,
        polarity="supports",
    )
    db.add(assertion)
    db.commit()
    return assertion


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract claims and score them.")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    engine = init_engine()
    db = SessionLocal()
    try:
        query = db.query(NormalizedText)
        if args.limit:
            query = query.limit(args.limit)
        normalized_rows = query.all()
        for row in normalized_rows:
            membership = db.execute(
                select(EventMembership).where(EventMembership.source_item_id == row.source_item_id)
            ).scalar_one_or_none()
            if membership is None:
                continue
            source_item = db.get(SourceItem, row.source_item_id)
            if source_item is None or source_item.is_filtered:
                continue

            extracted = extract_claims(row.normalized_text)
            for claim in extracted:
                claim_record = _ensure_claim(
                    db, membership.event_id, claim.normalized_text, claim.claim_type
                )
                _ensure_assertion(db, claim_record.id, row.source_item_id, claim.excerpt)
                create_assessment_if_missing(db, claim_record)
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
