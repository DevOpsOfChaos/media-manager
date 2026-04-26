from media_manager.core.gui_qt_refresh_plan import build_qt_refresh_plan
from media_manager.core.gui_qt_keyboard_router import build_keyboard_route_table, route_keyboard_shortcut


def test_refresh_plan_detects_theme_and_page_changes() -> None:
    plan = build_qt_refresh_plan(
        {"theme": {"theme": "modern-dark"}, "active_page_id": "dashboard"},
        {"theme": {"theme": "modern-light"}, "active_page_id": "people-review"},
    )

    assert plan["requires_full_rebuild"] is True
    assert plan["requires_page_rebuild"] is True
    assert plan["step_count"] >= 2


def test_keyboard_router_returns_safe_intents() -> None:
    table = build_keyboard_route_table([{"id": "people", "shortcut": "Ctrl+3", "intent": {"type": "navigate", "page_id": "people-review"}}])
    routed = route_keyboard_shortcut("Ctrl+3", table)

    assert routed["handled"] is True
    assert routed["intent"]["page_id"] == "people-review"
    assert routed["executes_immediately"] is False
