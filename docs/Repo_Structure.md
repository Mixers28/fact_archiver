evidence-ledger/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .editorconfig
├─ .env.example
├─ docker-compose.yml
├─ docs/
│  ├─ V1_SPEC.md
│  ├─ DATA_MODEL.md
│  ├─ CAPTURE_TIERS.md
│  ├─ SCORING_RULES.md
│  ├─ REVIEW_WORKFLOW.md
│  └─ THREAT_MODEL.md
│
├─ configs/
│  ├─ sources/
│  │  ├─ curated_sources.yaml          # hand-picked feeds + watch pages
│  │  ├─ publisher_families.yaml       # optional: syndication grouping (v2-ish)
│  │  └─ allow_deny_lists.yaml         # domains, paths, filetype limits
│  ├─ retention.yaml                   # retention tiers + caps
│  ├─ capture.yaml                     # tier rules, size caps, timeouts
│  └─ scoring.yaml                     # transparent scoring thresholds
│
├─ packages/
│  ├─ common/
│  │  ├─ src/
│  │  │  ├─ types/                     # shared TS/Python typings via jsonschema
│  │  │  ├─ schemas/                   # JSON Schemas for events/claims/artifacts
│  │  │  ├─ crypto/                    # hashing, merkle utils, signing stubs
│  │  │  ├─ text/                      # normalization, boilerplate stripping
│  │  │  └─ time/                      # date_key, timezone helpers
│  │  └─ tests/
│  │
│  ├─ ingestor/
│  │  ├─ src/
│  │  │  ├─ feeds/                     # RSS/Atom ingestion
│  │  │  ├─ watchers/                  # watch pages / curated URL pulls
│  │  │  ├─ dedupe/                    # canonical URL + similarity checks
│  │  │  ├─ jobs/                      # enqueue capture jobs
│  │  │  └─ cli/                       # `ingestor run --date ...`
│  │  └─ tests/
│  │
│  ├─ capture/
│  │  ├─ src/
│  │  │  ├─ tier1/                     # screenshot/PDF + text extraction
│  │  │  ├─ tier2/                     # WARC/WACZ capture hooks
│  │  │  ├─ playwright/                # browser harness + hardening
│  │  │  ├─ extractors/                # readability/text extraction
│  │  │  ├─ limits/                    # size caps, timeouts, media blocking
│  │  │  ├─ storage/                   # S3/minio client, path conventions
│  │  │  └─ cli/                       # `capture one <url> --tier 1`
│  │  └─ tests/
│  │
│  ├─ processor/
│  │  ├─ src/
│  │  │  ├─ clustering/                # event clustering
│  │  │  ├─ claims/                    # claim extraction + normalization
│  │  │  ├─ scoring/                   # status +
