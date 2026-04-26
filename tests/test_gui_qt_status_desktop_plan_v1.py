from __future__ import annotations

from media_manager.core.gui_qt_desktop_plan import build_qt_desktop_plan, summarize_qt_desktop_plan
from media_manager.core.gui_qt_status_presenter import build_qt_status_presenter


def _shell_model() -> dict[str, object]:
    return {
        "active_page_id": "dashboard",
        "window": {"title": "Media Manager", "width": 1200, "height": 800},
        "theme": {"theme": "modern-dark"},
        "navigation": [{"id": "dashboard", "label": "Dashboard"}, {"id": "people-review", "label": "People"}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": []},
        "status_bar": {"text": "Ready", "privacy": "Local only"},
    }


def test_status_presenter_is_safe_and_page_aware() -> None:
    status = build_qt_status_presenter(_shell_model())

    assert status["active_page_id"] == "dashboard"
    assert status["text"] == "Ready"
    assert status["safe_mode"] is True


def test_desktop_plan_composes_navigation_page_and_status() -> None:
    plan = build_qt_desktop_plan(_shell_model())

    assert plan["kind"] == "qt_desktop_plan"
    assert plan["navigation"]["item_count"] == 2
    assert plan["page_plan"]["layout"] == "dashboard_responsive_grid"
    assert plan["safe_runtime"]["executes_commands"] is False
    assert "Qt desktop plan" in summarize_qt_desktop_plan(plan)
