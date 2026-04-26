from media_manager.core.gui_qt_dashboard_visible_plan import build_qt_dashboard_visible_plan


def test_dashboard_visible_plan_has_hero_and_cards() -> None:
    page = {
        "page_id": "dashboard",
        "kind": "dashboard_page",
        "title": "Dashboard",
        "hero": {"title": "Welcome", "metrics": {"runs": 2}},
        "cards": [{"id": "runs", "title": "Runs"}],
        "activity": {"items": [{"title": "Recent"}]},
    }
    plan = build_qt_dashboard_visible_plan(page)
    assert plan["kind"] == "qt_dashboard_visible_plan"
    assert plan["summary"]["card_count"] == 1
    assert plan["sections"][0]["variant"] == "hero"
