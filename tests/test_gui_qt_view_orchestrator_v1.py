from media_manager.core.gui_qt_view_orchestrator import (
    apply_qt_view_action_to_model,
    build_qt_view_orchestration_state,
    plan_qt_view_action,
)


def _shell_model() -> dict:
    return {
        "active_page_id": "dashboard",
        "language": "en",
        "theme": {"theme": "modern-dark"},
        "application": {"title": "Media Manager"},
        "window": {"width": 1400, "height": 900},
        "navigation": [{"id": "dashboard", "active": True}, {"id": "people-review", "active": False}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "layout": "hero_card_grid", "cards": []},
        "status_bar": {"text": "Ready"},
        "capabilities": {"qt_shell": True, "executes_commands": False},
    }


def test_orchestration_state_contains_toolbar_and_validation() -> None:
    state = build_qt_view_orchestration_state(_shell_model())
    assert state["ready"] is True
    assert state["toolbar"]["action_count"] >= 1
    assert state["executes_commands"] is False


def test_action_plan_is_non_executing_and_builds_reload_plan() -> None:
    plan = plan_qt_view_action(_shell_model(), {"id": "open_people", "page_id": "people"})
    assert plan["intent"]["target_page_id"] == "people-review"
    assert plan["reload_plan"]["strategy"] == "page_refresh"
    assert plan["executes_immediately"] is False


def test_apply_view_action_updates_navigation_only() -> None:
    updated = apply_qt_view_action_to_model(_shell_model(), {"id": "open_people", "page_id": "people"})
    assert updated["active_page_id"] == "people-review"
    assert updated["navigation"][0]["active"] is False
    assert updated["navigation"][1]["active"] is True
    assert updated["executes_commands"] is False
