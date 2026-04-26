from media_manager.core.gui_qt_screen_map import build_qt_screen_map, normalize_screen_id


def test_normalize_screen_aliases() -> None:
    assert normalize_screen_id("people") == "people-review"
    assert normalize_screen_id("runs") == "run-history"


def test_screen_map_marks_active() -> None:
    payload = build_qt_screen_map(active_page_id="people")
    assert payload["active_page_id"] == "people-review"
    assert payload["active_screen"]["id"] == "people-review"
    assert payload["screen_count"] >= 6
