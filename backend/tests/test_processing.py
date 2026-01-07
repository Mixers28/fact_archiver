from app.text_utils import hash_text, normalize_text


def test_normalize_text_collapses_whitespace():
    raw = "Line one.\n\nLine two.\tTabbed."
    normalized = normalize_text(raw)
    assert normalized == "Line one. Line two. Tabbed."


def test_hash_text_is_deterministic():
    value = "same input"
    assert hash_text(value) == hash_text(value)
