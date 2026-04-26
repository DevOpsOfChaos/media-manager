from media_manager.core.gui_qt_renderer_blueprint import build_qt_renderer_blueprint

def test_renderer_blueprint_contains_sidebar_and_page() -> None:
    model = {
        "active_page_id": "dashboard",
        "window": {"title": "Media Manager"},
        "navigation": [{"id": "dashboard", "label": "Dashboard", "active": True}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": [{"id": "a", "title": "A"}]},
    }
    payload = build_qt_renderer_blueprint(model)
    assert payload["kind"] == "qt_renderer_blueprint"
    assert payload["widget_summary"]["widget_count"] >= 4
    assert payload["active_page_id"] == "dashboard"
