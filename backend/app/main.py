from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import lifespan
from app.db import get_db
from app.models import (
    Assessment,
    Claim,
    ClaimAssertion,
    Event,
    EventMembership,
    SourceItem,
    TransparencyLogEntry,
)
from app.settings import get_cors_origins

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/verification", response_class=HTMLResponse)
def verification_page(db: Session = Depends(get_db)):
    entries = (
        db.execute(select(TransparencyLogEntry).order_by(TransparencyLogEntry.created_at.desc()))
        .scalars()
        .all()
    )
    rows = "\n".join(
        f"<tr><td>{e.created_at}</td><td>{e.previous_root or ''}</td><td>{e.merkle_root}</td></tr>"
        for e in entries
    )
    html = f"""
    <html>
      <head>
        <title>Verification</title>
      </head>
      <body>
        <h1>Transparency Log</h1>
        <p>Each entry links to the previous root to prove append-only history.</p>
        <table border="1" cellpadding="6" cellspacing="0">
          <thead>
            <tr><th>Created At</th><th>Previous Root</th><th>Merkle Root</th></tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
        <h2>Verification Steps</h2>
        <ol>
          <li>Recompute daily hashes for SourceItems, Artifacts, and Assessments.</li>
          <li>Build a Merkle root from the sorted hashes.</li>
          <li>Compare with the recorded Merkle root for the same date.</li>
          <li>Verify each entry links to the previous root.</li>
        </ol>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


class ReviewOverrideRequest(BaseModel):
    status: str = Field(..., min_length=1)
    score: float | None = None
    rationale: list[str] | None = None


def _parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date format (YYYY-MM-DD)") from exc


def _latest_assessments_subquery():
    return (
        select(Assessment.claim_id, func.max(Assessment.created_at).label("max_created"))
        .group_by(Assessment.claim_id)
        .subquery()
    )


@app.get("/api/days")
def get_days(start: str | None = None, end: str | None = None, db: Session = Depends(get_db)):
    if not start or not end:
        raise HTTPException(status_code=400, detail="start and end are required (YYYY-MM-DD)")
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end must be >= start")
    rows = (
        db.execute(
            select(Event.date_key, func.count(Event.id))
            .where(Event.date_key >= start, Event.date_key <= end)
            .group_by(Event.date_key)
            .order_by(Event.date_key)
        )
        .all()
    )
    counts = {row[0]: row[1] for row in rows}
    days = []
    cursor = start_date
    while cursor <= end_date:
        key = cursor.strftime("%Y-%m-%d")
        days.append({"date": key, "event_count": counts.get(key, 0)})
        cursor += timedelta(days=1)
    return {"days": days}


@app.get("/api/days/{date_key}")
def get_day(date_key: str, db: Session = Depends(get_db)):
    _parse_date(date_key)
    events = (
        db.execute(select(Event).where(Event.date_key == date_key).order_by(Event.created_at.desc()))
        .scalars()
        .all()
    )

    latest_assessments = _latest_assessments_subquery()
    review_claims = (
        db.execute(
            select(Claim, Assessment)
            .join(latest_assessments, latest_assessments.c.claim_id == Claim.id)
            .join(
                Assessment,
                (Assessment.claim_id == latest_assessments.c.claim_id)
                & (Assessment.created_at == latest_assessments.c.max_created),
            )
            .join(Event, Claim.event_id == Event.id)
            .where(Event.date_key == date_key)
            .where(Assessment.status.in_(["Unverified", "Contested"]))
        )
        .all()
    )

    return {
        "date": date_key,
        "events": [
            {
                "id": str(event.id),
                "title": event.title,
                "importance_score": event.importance_score,
            }
            for event in events
        ],
        "review_queue": [
            {
                "claim_id": str(claim.id),
                "event_id": str(claim.event_id),
                "normalized_text": claim.normalized_text,
                "status": assessment.status,
                "score": assessment.score,
            }
            for claim, assessment in review_claims
        ],
    }


@app.get("/api/events/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event not found")

    sources = (
        db.execute(
            select(SourceItem)
            .join(EventMembership, EventMembership.source_item_id == SourceItem.id)
            .where(EventMembership.event_id == event.id)
        )
        .scalars()
        .all()
    )

    latest_assessments = _latest_assessments_subquery()
    claims = (
        db.execute(
            select(Claim, Assessment)
            .join(latest_assessments, latest_assessments.c.claim_id == Claim.id)
            .join(
                Assessment,
                (Assessment.claim_id == latest_assessments.c.claim_id)
                & (Assessment.created_at == latest_assessments.c.max_created),
            )
            .where(Claim.event_id == event.id)
        )
        .all()
    )

    grouped: dict[str, list[dict]] = {}
    for claim, assessment in claims:
        grouped.setdefault(assessment.status, []).append(
            {
                "id": str(claim.id),
                "normalized_text": claim.normalized_text,
                "score": assessment.score,
                "rationale": assessment.rationale,
            }
        )

    return {
        "id": str(event.id),
        "title": event.title,
        "date_key": event.date_key,
        "sources": [
            {
                "id": str(source.id),
                "publisher": source.publisher,
                "url": source.url,
                "published_at": source.published_at.isoformat() if source.published_at else None,
            }
            for source in sources
        ],
        "claims_by_status": grouped,
    }


@app.post("/api/claims/{claim_id}/override")
def override_claim(claim_id: str, payload: ReviewOverrideRequest, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="claim not found")
    assessment = Assessment(
        claim_id=claim.id,
        model_version="human",
        status=payload.status,
        score=payload.score,
        rationale=payload.rationale or [],
        computed_signals={},
    )
    db.add(assessment)
    db.commit()
    return {"assessment_id": str(assessment.id)}
