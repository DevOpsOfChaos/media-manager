from media_manager.core.gui_qt_action_result import build_qt_action_result, summarize_qt_action_results
from media_manager.core.gui_qt_toolbar_actions import build_qt_toolbar_actions, merge_qt_toolbar_actions


def test_action_result_summarizes_statuses() -> None:
    accepted = build_qt_action_result("open_people", status="accepted")
    blocked = build_qt_action_result("apply", status="blocked", problems=["confirmation missing"])
    summary = summarize_qt_action_results([accepted, blocked])
    assert accepted["notification"]["level"] == "success"
    assert blocked["problem_count"] == 1
    assert summary["blocked_count"] == 1


def test_toolbar_actions_are_safe_and_page_aware() -> None:
    toolbar = build_qt_toolbar_actions({"page_id": "people-review", "quick_actions": []}, language="de")
    assert toolbar["page_id"] == "people-review"
    assert toolbar["action_count"] >= 2
    assert toolbar["confirmation_count"] >= 1
    assert all(action["executes_immediately"] is False for action in toolbar["actions"])


def test_toolbar_merge_deduplicates_actions() -> None:
    merged = merge_qt_toolbar_actions(
        [{"id": "refresh", "label": "Refresh"}],
        [{"id": "refresh", "label": "Refresh duplicate"}, {"id": "settings", "label": "Settings"}],
    )
    assert merged["action_count"] == 2
