import hashlib
import os
from datetime import datetime

from app.settings import get_artifact_root, get_max_capture_bytes


def build_artifact_path(
    date_key: str, publisher: str | None, source_item_id: str, artifact_type: str, ext: str
) -> str:
    safe_publisher = (publisher or "unknown").replace("/", "_").strip() or "unknown"
    filename = f"{artifact_type}.{ext}"
    return os.path.join(get_artifact_root(), date_key, safe_publisher, source_item_id, filename)


def write_bytes(path: str, data: bytes) -> tuple[int, str]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    size = os.path.getsize(path)
    if size > get_max_capture_bytes():
        os.remove(path)
        raise ValueError(f"artifact exceeds max size: {size} bytes")
    sha256 = hashlib.sha256(data).hexdigest()
    return size, sha256


def write_text(path: str, text: str) -> tuple[int, str]:
    data = text.encode("utf-8")
    return write_bytes(path, data)


def write_text_bytes(path: str, data: bytes) -> tuple[int, str]:
    return write_bytes(path, data)


def date_key_for(dt: datetime | None) -> str:
    if dt is None:
        return datetime.utcnow().strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m-%d")
