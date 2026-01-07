import argparse
from datetime import datetime, timezone

from app.db import SessionLocal, init_engine
from app.transparency import append_daily_log_entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a daily transparency log entry.")
    parser.add_argument("--date", help="YYYY-MM-DD (defaults to today UTC)", default=None)
    args = parser.parse_args()

    date_key = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    engine = init_engine()
    db = SessionLocal()
    try:
        entry = append_daily_log_entry(db, date_key)
        print(f"appended log root: {entry.merkle_root}")
    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
