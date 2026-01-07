import argparse
import html as html_lib
import re

from app.db import SessionLocal, init_engine
from app.models import Artifact, SourceItem
from app.processing import list_unclustered_items, upsert_normalized_text, cluster_source_items

_TAG_RE = re.compile(r"<[^>]+>")


def _load_text_artifact(db, source_item_id):
    return (
        db.query(Artifact)
        .filter(Artifact.source_item_id == source_item_id, Artifact.type.in_(["text", "html"]))
        .one_or_none()
    )


def _extract_text(artifact: Artifact) -> str:
    if artifact.type == "html":
        with open(artifact.storage_uri, "rb") as handle:
            raw = handle.read()
        decoded = raw.decode("utf-8", errors="ignore")
        stripped = _TAG_RE.sub(" ", decoded)
        return html_lib.unescape(stripped)
    with open(artifact.storage_uri, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def main() -> None:
    parser = argparse.ArgumentParser(description="Process SourceItems for Phase 3.")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--cluster", action="store_true")
    args = parser.parse_args()

    engine = init_engine()
    db = SessionLocal()
    try:
        if args.normalize:
            items = (
                db.query(SourceItem)
                .filter(SourceItem.capture_status == "captured")
                .filter(SourceItem.is_filtered.is_(False))
                .all()
            )
            for item in items:
                artifact = _load_text_artifact(db, item.id)
                if not artifact:
                    continue
                raw_text = _extract_text(artifact)
                upsert_normalized_text(db, item, raw_text)

        if args.cluster:
            items = list_unclustered_items(db)
            cluster_source_items(db, items)
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
