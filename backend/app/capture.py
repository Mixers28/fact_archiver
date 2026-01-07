from __future__ import annotations

from datetime import datetime

from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_engine
from app.models import Artifact, SourceItem
from app.settings import get_capture_timeout_ms
from app.storage import build_artifact_path, date_key_for, write_bytes, write_text


def capture_source_item(db: Session, source_item_id: str) -> int:
    source_item = db.get(SourceItem, source_item_id)
    if source_item is None:
        raise ValueError(f"source_item not found: {source_item_id}")

    source_item.capture_status = "capturing"
    db.commit()

    created = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(source_item.url, timeout=get_capture_timeout_ms(), wait_until="networkidle")

        date_key = date_key_for(source_item.published_at or datetime.utcnow())

        screenshot_path = build_artifact_path(
            date_key, source_item.publisher, str(source_item.id), "screenshot", "png"
        )
        screenshot_bytes = page.screenshot(full_page=True)
        size, sha256 = write_bytes(screenshot_path, screenshot_bytes)
        db.add(
            Artifact(
                source_item_id=source_item.id,
                type="screenshot",
                storage_uri=screenshot_path,
                bytes=size,
                sha256=sha256,
                tool_version="playwright-python",
            )
        )
        created += 1

        pdf_path = build_artifact_path(
            date_key, source_item.publisher, str(source_item.id), "pdf", "pdf"
        )
        pdf_bytes = page.pdf()
        size, sha256 = write_bytes(pdf_path, pdf_bytes)
        db.add(
            Artifact(
                source_item_id=source_item.id,
                type="pdf",
                storage_uri=pdf_path,
                bytes=size,
                sha256=sha256,
                tool_version="playwright-python",
            )
        )
        created += 1

        body_text = page.inner_text("body")
        text_path = build_artifact_path(
            date_key, source_item.publisher, str(source_item.id), "text", "txt"
        )
        size, sha256 = write_text(text_path, body_text)
        db.add(
            Artifact(
                source_item_id=source_item.id,
                type="text",
                storage_uri=text_path,
                bytes=size,
                sha256=sha256,
                tool_version="playwright-python",
            )
        )
        created += 1

        context.close()
        browser.close()

    source_item.capture_status = "captured"
    db.commit()
    return created


def capture_source_item_job(source_item_id: str) -> int:
    engine = init_engine()
    db = SessionLocal()
    try:
        return capture_source_item(db, source_item_id)
    finally:
        db.close()
        engine.dispose()
