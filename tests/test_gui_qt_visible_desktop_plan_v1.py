from media_manager.core.gui_qt_visible_desktop_plan import build_qt_visible_desktop_plan, desktop_plan_is_ready


def test_visible_desktop_plan_combines_navigation_and_page() -> None:
    plan = build_qt_visible_desktop_plan(
        {
            "active_page_id": "dashboard",
            "window": {"title": "Media Manager"},
            "theme": {"theme": "modern-dark"},
            "navigation": [{"id": "dashboard", "label": "Dashboard", "active": True}],
            "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": []},
            "status_bar": {"text": "Ready"},
        }
    )
    assert plan["summary"]["navigation_count"] == 1
    assert plan["navigation"][0]["shortcut"] == "Ctrl+1"
    assert desktop_plan_is_ready(plan)
