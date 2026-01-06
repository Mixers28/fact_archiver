# Project Context – Long-Term Memory (LTM)

> High-level design, tech decisions, constraints for this project.  
> This is the **source of truth** for agents and humans.

<!-- SUMMARY_START -->
**Summary (auto-maintained by Agent):**
- Evidence Ledger (Fact Archiver): daily calendar-based evidence ledger capturing who said what, when, with proof artifacts and claim-level statuses.
- V1 scope: ingest curated sources, tiered capture (screenshot/PDF + text; selective WARC/WACZ), claim extraction, event clustering, append-only transparency log, review queue UI.
- Architecture: Ingestor → Capture → Processor → Ledger Store (Postgres + object store) → Reviewer/Public UI; deterministic pipeline and append-only log are non-negotiable.
<!-- SUMMARY_END -->

---

## 1. Project Overview

- **Name:** Evidence Ledger (Fact Archiver)
- **Owner:** TBD
- **Purpose:** A daily, calendar-based evidence ledger that preserves proof artifacts, extracts claims, and tracks claim status over time without rewriting history (append-only).
- **Primary Stack:** TBD (likely Postgres, S3-compatible object storage, Playwright capture, Next.js UI).
- **Target Platforms:** Web UI + backend services for ingestion/capture/processing.

---

## 2. Core Design Pillars

- Claims not facts: store statements + evidence + assessments.
- Append-only: never delete/overwrite; supersede with new records.
- Show your work: confidence rationale is human-readable and versioned.
- Tiered capture: cheap proof for most, heavy capture for a small subset.
- Deterministic and verifiable pipeline.

---

## 3. Technical Decisions & Constraints

- Language(s): Backend language TBD (Python or Node suggested).
- Framework(s): Frontend likely Next.js (not locked).
- Database / storage: Postgres for ledger; S3-compatible object store for artifacts.
- Hosting / deployment: TBD (local dev + optional cloud).
- Non-negotiable constraints:
  - Deterministic ingestion pipeline and append-only transparency log.
  - Tiered capture with size limits; skip video/audio downloads in V1.
  - Evidence-based scoring; no "truth" declaration or political bias scoring.

---

## 4. Memory Hygiene (Drift Guards)

- Keep this summary block current and <= 300 tokens.
- Move stable decisions into the Change Log so they persist across sessions.
- Keep NOW to 5–12 active tasks; archive or remove completed items.
- Roll up SESSION_NOTES into summaries weekly (or every few sessions).

---

## 5. Architecture Snapshot

- Ingestor: RSS/curated URL intake → SourceItems.
- Capture Service: artifacts (screenshot/PDF/text; selective WARC/WACZ) + hashes.
- Processor: text normalization, dedup, event clustering, claim extraction, scoring.
- Ledger Store: Postgres + object store + append-only transparency log.
- UI: Reviewer queue + Public Calendar/Event pages + verification view.

---

## 6. Links & Related Docs

- Roadmap: TBD
- Spec: docs/Spec.md
- Design docs: docs/MCP_LOCAL_DESIGN.md, docs/AGENT_SESSION_PROTOCOL.md
- Product / UX docs: docs/PROJECT_CONTEXT.md, docs/NOW.md

---

## 7. Change Log (High-Level Decisions)

Use this section for **big decisions** only:

- `2026-01-06` – Adopted the Evidence Ledger V1 spec as current scope and memory baseline.
