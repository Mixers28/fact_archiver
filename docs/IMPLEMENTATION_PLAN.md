# Implementation Plan (Coder)

This plan mirrors the approved V1 phases and tracks execution progress.

## Phase 0 — Defaults & cost-first setup
- [ ] Confirm stack defaults in PROJECT_CONTEXT.
- [ ] Add local dev run steps.

## Phase 1 — Core data model + API skeleton
- [x] Add SQLAlchemy models for all Spec entities.
- [x] Add Alembic migration for initial schema.
- [x] Add FastAPI app skeleton with lifespan and health check.

## Phase 2 — Ingestion + Tier 1 capture
- [x] Implement RSS/curated URL ingestion to SourceItems.
- [x] Implement Playwright capture worker + hashing.
- [x] Store artifacts in object storage with stable naming.

## Phase 3 — Processing + event clustering
- [x] Normalize text + dedup.
- [x] Basic event clustering + manual merge/split hooks.

## Phase 4 — Claims + scoring
- [x] Extract claims + assertions.
- [x] Score and create versioned assessments with rationale.

## Phase 5 — Transparency log
- [x] Daily Merkle root + append-only log.
- [x] Verification endpoint/page.

## Phase 6 — Reviewer + public UI
- [x] Calendar/day view + event page.
- [x] Reviewer queue + overrides.
