import argparse

from app.capture import (
    capture_source_item,
    capture_source_item_job,
    capture_text_only,
    capture_text_only_job,
)
from app.db import SessionLocal, init_engine
from app.ingest import ingest_rss_from_file, ingest_urls_from_file
from app.models import SourceItem
from app.queue import get_queue
from app.settings import get_rss_path, get_urls_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest sources into SourceItems.")
    parser.add_argument("--rss-path", default=get_rss_path())
    parser.add_argument("--urls-path", default=get_urls_path())
    parser.add_argument("--enqueue", action="store_true")
    parser.add_argument("--capture-now", action="store_true")
    parser.add_argument("--text-only", action="store_true")
    args = parser.parse_args()

    engine = init_engine()
    db = SessionLocal()
    try:
        rss_result = ingest_rss_from_file(db, args.rss_path)
        url_result = ingest_urls_from_file(db, args.urls_path)
        print(f"RSS: created={rss_result.created} skipped={rss_result.skipped}")
        print(f"URL: created={url_result.created} skipped={url_result.skipped}")

        if args.enqueue:
            queue = get_queue()
            pending = (
                db.query(SourceItem)
                .filter(SourceItem.capture_status == "pending")
                .filter(SourceItem.is_filtered.is_(False))
                .all()
            )
            for item in pending:
                if args.text_only:
                    queue.enqueue(capture_text_only_job, str(item.id))
                else:
                    queue.enqueue(capture_source_item_job, str(item.id))
            print(f"Enqueued {len(pending)} capture jobs")
        elif args.capture_now:
            pending = (
                db.query(SourceItem)
                .filter(SourceItem.capture_status == "pending")
                .filter(SourceItem.is_filtered.is_(False))
                .all()
            )
            for item in pending:
                if args.text_only:
                    capture_text_only(db, str(item.id))
                else:
                    capture_source_item(db, str(item.id))
            print(f"Captured {len(pending)} items")
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
