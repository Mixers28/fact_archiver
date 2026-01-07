import argparse

from app.db import SessionLocal, init_engine
from app.models import Artifact, SourceItem
from app.processing import list_unclustered_items, upsert_normalized_text, cluster_source_items


def _load_text_artifact(db, source_item_id):
    return (
        db.query(Artifact)
        .filter(Artifact.source_item_id == source_item_id, Artifact.type == "text")
        .one_or_none()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Process SourceItems for Phase 3.")
    parser.add_argument("--normalize", action="store_true")
    parser.add_argument("--cluster", action="store_true")
    args = parser.parse_args()

    engine = init_engine()
    db = SessionLocal()
    try:
        if args.normalize:
            items = db.query(SourceItem).filter(SourceItem.capture_status == "captured").all()
            for item in items:
                artifact = _load_text_artifact(db, item.id)
                if not artifact:
                    continue
                with open(artifact.storage_uri, "r", encoding="utf-8") as handle:
                    raw_text = handle.read()
                upsert_normalized_text(db, item, raw_text)

        if args.cluster:
            items = list_unclustered_items(db)
            cluster_source_items(db, items)
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
