import os


def get_database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/fact_archiver",
    )


def get_artifact_root() -> str:
    return os.environ.get("ARTIFACT_ROOT", "./artifacts")


def get_capture_timeout_ms() -> int:
    return int(os.environ.get("CAPTURE_TIMEOUT_MS", "45000"))


def get_max_capture_bytes() -> int:
    return int(os.environ.get("MAX_CAPTURE_BYTES", "52428800"))


def get_redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


def get_rss_path() -> str:
    return os.environ.get("INGEST_RSS_PATH", "./data/feeds.txt")


def get_urls_path() -> str:
    return os.environ.get("INGEST_URLS_PATH", "./data/urls.txt")


def get_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
