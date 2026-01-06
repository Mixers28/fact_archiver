V1 SPEC — Evidence Ledger (Source-of-Truth by Evidence, Not Authority)
0) One-line

A daily, calendar-based evidence ledger that captures “who said what, when,” preserves proof artifacts, extracts claim-level statements, and assigns a transparent confidence/status that can evolve over time without rewriting history (append-only).

1) Goals (V1)

G1 — Preserve evidence

For selected sources each day, store proof artifacts so later edits/deletions are detectable.

G2 — Track narrative drift

Detect and display changes: new claims, corrections, retractions, and contradictions across sources over time.

G3 — Claim-level confidence

Convert articles into atomic claims and label each claim with a status + rationale.

G4 — Human-doable daily review

A review queue you can finish in ~15–30 minutes/day.

G5 — Deterministic + tamper-evident

Ingestion is reproducible; archived artifacts are hashed; changes are append-only and verifiable.

2) Non-Goals (V1)

“We declare the Truth.” (No — we assess evidence strength.)

Full internet crawl / comprehensive coverage.

Video/audio archiving at scale (storage + legal risk).

Perfect NLP extraction (good-enough claims, with human override).

Political “bias scoring” (keep it evidence-based, not ideology-based).

3) Core Principles

Claims not facts: store statements + evidence + assessments.

Append-only: never delete or overwrite; supersede with newer records.

Show your work: confidence rationale is human-readable and versioned.

Tiered capture: cheap proof for most, heavy capture for the few that matter.

4) User Stories

“On a date, show me key events and what was known then.”

“Show all sources covering Event X and how they differ.”

“Show claim timeline: when it appeared, got corroborated, or was retracted.”

“Give me a daily queue of items that need judgment.”

“Export a proof bundle for Event X (hashes + artifacts list).”

5) V1 Scope (What we build)
5.1 Calendar UI (the product)

Calendar view → click a day → “Daily Ledger”

Daily Ledger shows:

Top Events (clusters)

Review Queue (unverified/contested/changed)

Recently corrected/retracted claims

5.2 Event pages

Event summary (machine-generated + optional human blurb)

Source list (publisher, timestamp, captured artifacts)

Claim list (grouped by status)

Timeline (claim state transitions)

Evidence links (screenshots/PDF + extracted text; WARC/WACZ for high-importance)

5.3 Minimal public sustainability

“Support this project” section (Ko-fi style link/button)

6) Architecture (V1)

Components

Ingestor

Inputs: RSS feeds, curated URL lists, and optional “watch pages”

Output: SourceItems (URL + metadata)

Capture Service

Produces artifacts per SourceItem (tiered capture)

Computes hashes

Stores artifacts in object storage

Processor

Text extraction + canonicalization

Dedup detection

Event clustering

Claim extraction

Confidence scoring + rationale

Ledger Store

Relational DB (events/claims/assessments)

Object store (artifacts)

Append-only transparency log (Merkle root chain)

Reviewer UI

Daily queue

Claim status override + rationale editor

Promote items to Tier 2 capture

Public Read UI

Calendar + event pages

Verification page (log roots + hash checks)

7) Data Model (Minimal)
Entities

SourceItem

id, url, canonical_url, publisher, published_at (if known), discovered_at

fetch_headers, content_type, language

capture_tier (1/2), capture_status

Artifact

id, source_item_id

type: screenshot | pdf | text | html | warc/wacz | headers

storage_uri, bytes, sha256, created_at

tool_version (capture tool + version)

Event

id, title, date_key (YYYY-MM-DD), created_at

importance_score, tags (geo/politics/econ/etc)

EventMembership

event_id, source_item_id, confidence (membership strength)

Claim

id, event_id

normalized_text (canonical claim)

claim_type: who/what/when/where/why/number/quote

entities (optional), numeric_fields (optional)

ClaimAssertion

claim_id, source_item_id

extracted_span (start/end offsets) OR excerpt (short)

polarity: supports/denies/neutral

assertion_time (source published/discovered)

Assessment (versioned)

id, claim_id, model_version, created_at

status: Unverified | Corroborated | Confirmed | Contested | Retracted

score (0–1)

rationale (human-readable bullets)

computed_signals (json)

TransparencyLogEntry

id, previous_root, merkle_root, created_at

includes hashes of (source_item + artifacts + assessment snapshots)

8) Capture Strategy (Tiered)
Tier 1 (default, low-cost)

For every selected URL:

Metadata record

Extracted text (normalized)

Full-page screenshot or print-to-PDF

SHA-256 for each artifact

Tier 2 (selective, high-value)

For “high importance / high dispute / likely to change”:

WARC/WACZ capture (replayable)

Optional secondary screenshot after page loads fully

Sign the package (optional in V1; store signing key plan)

V1 rule of thumb

Tier 2 should be ~5–15% of captured URLs.

Hard limits (V1)

Skip embedded video/audio downloads.

Cap total bytes per capture (e.g., 50–100 MB) to avoid explosions.

9) Determinism + Tamper Evidence
Deterministic pipeline (V1)

Normalize extracted text (strip boilerplate; stable whitespace rules)

Stable claim ID = hash(normalized_claim + event_id + claim_type)

Stable artifact naming = {date}/{publisher}/{source_item_id}/{artifact_type}

Append-only transparency log

Every day (or every N ingests), compute Merkle root over:

SourceItem fields (canonical subset)

Artifact hashes

Assessment snapshot hashes

Store previous_root -> new_root chain.

Public page displays daily roots and verification instructions.

10) Event Clustering (V1)

Goal: group sources talking about the same story.

Use simple similarity:

Title similarity + entity overlap + time proximity (within 24–72 hours)

Start conservative:

Better to split than incorrectly merge in V1.

Allow reviewer to merge/split events manually.

11) Claim Extraction (V1)

Start simple:

Extract:

Headline claim

Lead paragraph key sentences

Quoted statements (“X said…”)

Numeric claims (“N people…”, “$X…”, dates)

Normalize claims:

Remove attribution clauses into ClaimAssertion (so the claim is “X happened” and assertion says “Outlet A claims this”).

12) Confidence Scoring (Transparent)

Each claim gets a status + score derived from signals:

Signals (V1)

independent_sources_count (excluding syndication)

source_diversity (publisher families)

primary_evidence_present (official doc, filing, direct statement link)

contradiction_count (credible sources deny)

correction_or_retraction_seen (publisher correction)

time_since_first_seen (early reports are noisier)

Mapping to statuses (example)

Confirmed: primary evidence present + ≥2 independent corroborations, low contradiction

Corroborated: ≥2 independent corroborations, no strong primary doc

Contested: contradiction_count ≥1 among credible sources

Retracted: original source retracts/corrects core claim

Unverified: single-source or weak evidence

Always show rationale bullets:

“Corroborated by 3 independent outlets”

“No primary document linked”

“Contested: Outlet B reports denial”

Reviewer can override status, but override becomes a new Assessment version (append-only).

13) Daily Review Workflow

Queue generation

New high-importance events

Claims that changed status since yesterday

Claims flagged contested/unverified with high reach

Corrections/retractions detected

Reviewer actions

Promote source/event to Tier 2 capture

Merge/split events

Edit claim normalization (optional)

Override status with rationale (creates new Assessment)

Target: <30 minutes/day.

14) UI Requirements (V1)
Calendar

Heatmap indicator (how many key events that day)

Daily Ledger (day view)

Top Events (by importance)

“Needs review” queue

“Status changes” list (claim-level)

Event page

Summary (auto + editable)

Sources (with timestamps + artifact links)

Claims by status with score + rationale

Timeline view (status over time)

Verification box: hashes + log root reference

15) Storage & Retention Policy (V1 defaults)

Retention tiers

Tier 1 artifacts: keep indefinitely for “key events”; keep 90–180 days for low-importance (configurable)

Tier 2 artifacts: keep indefinitely (selective set)

Dedup

If two captures produce same text hash, store once (link references).

Store raw artifact hashes even if deduped.

16) Security & Abuse Controls

Rate limit ingestion endpoints

Signed admin reviewer actions

Audit log of reviewer edits (append-only)

Backups of DB + object store

Avoid storing personal data from social posts in V1 unless explicitly curated

17) Tech Choices (suggested, not mandatory)

DB: Postgres

Object store: S3-compatible (MinIO locally, S3 in cloud)

Queue: Redis/RQ or RabbitMQ

Capture:

Headless browser (Playwright) for screenshots/PDF

Optional Browsertrix/Webrecorder stack for WACZ

Backend: Node or Python (choose based on your comfort)

Frontend: Next.js calendar + event pages

18) MVP Milestones (tight)

M1 — Ledger skeleton

Calendar + day view + source list

M2 — Tier 1 capture + hashing

screenshot/PDF + extracted text stored + hash display

M3 — Event clustering

basic clustering + manual merge/split

M4 — Claim extraction + scoring

claim list + statuses + rationale

M5 — Append-only log

daily Merkle root chain + verification page

19) Open Questions (parked for V2 unless easy)

Publisher family detection (to avoid counting syndication as independent)

Better primary-evidence detection

Community mirroring (IPFS) and timestamping proofs (OpenTimestamps)

Public API

20) Definition of Done (V1)

You can pick a date and reliably see:

events

sources

archived proof artifacts

claims + status + rationale

what changed since prior days

A third party can verify:

artifact hashes match what was logged

the transparency log is append-only (roots chain)