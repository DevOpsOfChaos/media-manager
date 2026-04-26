from media_manager.core.gui_qt_page_state_summary import build_qt_page_state_summary, build_qt_shell_state_summary
from media_manager.core.gui_qt_reload_coordinator import build_qt_reload_plan, compare_qt_state_for_reload


def test_page_and_shell_state_summary_detect_attention() -> None:
    page = {"page_id": "people-review", "kind": "people_review_page", "title": "People", "layout": "review", "empty_state": {"title": "Empty"}}
    shell = {"active_page_id": "people-review", "language": "en", "theme": {"theme": "modern-dark"}, "navigation": [{"id": "people-review", "enabled": True}], "page": page, "capabilities": {"qt_shell": True, "executes_commands": False}}
    page_summary = build_qt_page_state_summary(page)
    shell_summary = build_qt_shell_state_summary(shell)
    assert page_summary["needs_attention"] is True
    assert shell_summary["page_summary"]["page_id"] == "people-review"
    assert shell_summary["executes_commands"] is False


def test_reload_plan_distinguishes_strategies() -> None:
    assert build_qt_reload_plan(["status"])["strategy"] == "status_refresh"
    assert build_qt_reload_plan(["page"])["strategy"] == "page_refresh"
    assert build_qt_reload_plan(["theme"])["strategy"] == "full_rebuild"
    assert build_qt_reload_plan([])["strategy"] == "noop"


def test_compare_state_for_reload_detects_theme_change() -> None:
    previous = {"active_page_id": "dashboard", "theme": {"theme": "modern-dark"}}
    current = {"active_page_id": "dashboard", "theme": {"theme": "modern-light"}}
    plan = compare_qt_state_for_reload(previous, current)
    assert plan["strategy"] == "full_rebuild"
