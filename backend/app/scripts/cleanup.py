import argparse
from datetime import datetime, timedelta, timezone

from app.db import SessionLocal, init_engine
from app.models import SourceItem
from app.significance import is_significant


def main() -> None:
    parser = argparse.ArgumentParser(description="Mark recent non-significant items as filtered.")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    engine = init_engine()
    db = SessionLocal()
    try:
        candidates = (
            db.query(SourceItem)
            .filter(SourceItem.discovered_at >= cutoff)
            .filter(SourceItem.is_filtered.is_(False))
            .all()
        )
        if not candidates:
            print("No recent SourceItems to evaluate.")
            return

        updated = 0
        for item in candidates:
            if item.is_significant is None:
                item.is_significant = is_significant([], item.title or "", "")
            if item.is_significant is False:
                item.is_filtered = True
                item.capture_status = "filtered"
                updated += 1

        if args.dry_run:
            print(f"Dry run: would filter {updated} SourceItems.")
            db.rollback()
            return

        db.commit()
        print(f"Filtered {updated} SourceItems.")
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
