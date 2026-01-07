# Fact Archiver (Evidence Ledger)

A daily, calendar-based evidence ledger that captures who said what, when, preserves proof artifacts, and tracks claim status over time with an append-only history.

## V1 Scope

- Ingest curated sources (RSS + URL lists).
- Tiered capture: screenshots/PDF + extracted text for most; selective WARC/WACZ for high-importance items.
- Claim extraction and status scoring with transparent rationales.
- Event clustering and timeline views.
- Append-only transparency log with verifiable hashes.

## Repo Layout

- `docs/Spec.md` — Canonical product spec.
- `docs/PROJECT_CONTEXT.md` — Long-term memory and decisions.
- `docs/NOW.md` — Current focus and near-term tasks.
- `docs/SESSION_NOTES.md` — Session log (append-only).

## Deployment Notes

Backend (Railway):
- Root directory: `backend`
- Start command: `sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"`
- Env vars:
  - `DATABASE_URL` (Railway Postgres internal URL)
  - `CORS_ORIGINS` (comma-separated frontend origins)
  - `NIXPACKS_PYTHON_VERSION=3.12`

Frontend (Vercel):
- Root directory: `frontend`
- Env vars:
  - `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-host>`

Database migrations:
```bash
alembic upgrade head
```

## Git Intro (this repo)

First-time setup:
```bash
git clone https://github.com/Mixers28/fact_archiver.git
cd fact_archiver
```

Common workflow:
```bash
git checkout -b feature/your-change
git status -sb
git add .
git commit -m "Describe the change"
git push -u origin feature/your-change
```

Push the main branch (if you work directly on `main`):
```bash
git push -u origin main
```
