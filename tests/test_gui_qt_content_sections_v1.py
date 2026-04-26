from media_manager.core.gui_qt_content_sections import build_qt_content_sections


def test_dashboard_sections_include_hero_and_cards() -> None:
    payload = build_qt_content_sections({"page_id": "dashboard", "kind": "dashboard_page", "hero": {"title": "Hi"}, "cards": [{"id": "a"}]})
    ids = [item["id"] for item in payload["sections"]]
    assert ids[:2] == ["hero", "cards"]


def test_people_sections_include_queue_detail_assets() -> None:
    payload = build_qt_content_sections({"page_id": "people-review", "kind": "people_review_page", "groups": [{"group_id": "g1"}], "detail": {}})
    assert payload["section_count"] == 3
