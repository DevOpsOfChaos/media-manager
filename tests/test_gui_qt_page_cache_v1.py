from media_manager.core.gui_qt_page_cache import build_page_cache, build_page_cache_entry, find_cached_page


def test_page_cache_finds_entries_by_key() -> None:
    entry = build_page_cache_entry("dashboard", {"kind": "page"}, language="de", query="x")
    cache = build_page_cache([entry])
    assert cache["entry_count"] == 1
    found = find_cached_page(cache, entry["key"])
    assert found is not None
    assert found["page_id"] == "dashboard"
