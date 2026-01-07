from app.significance import is_significant


def test_significant_category_overrides_exclude_tokens():
    assert is_significant(["Politics"], "Some title", "") is True


def test_excluded_category_is_filtered():
    assert is_significant(["Sports"], "Big match", "") is False


def test_whitelist_phrase_in_title_is_significant():
    assert is_significant([], "Central bank signals rate pause", "") is True


def test_excluded_phrase_in_title_is_filtered():
    assert is_significant([], "Opinion: why this matters", "") is False
