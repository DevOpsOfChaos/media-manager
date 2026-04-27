from __future__ import annotations


def sample_dashboard(*, ready: bool = True, blocked: int = 0, incomplete: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_dashboard",
        "active_page_id": "people-review",
        "ready_for_runtime_review": ready,
        "status_strip": {
            "badges": [{"state": "ready"}, {"state": "ready"}],
            "summary": {"badge_count": 2, "blocked_count": blocked, "incomplete_count": incomplete},
        },
        "trend": {
            "points": [{"ready": False}, {"ready": True}],
            "summary": {"entry_count": 2, "direction": "improved"},
        },
        "cards": [
            {"id": "current-report", "title": "Current runtime smoke", "metric": "ready"},
            {"id": "history", "title": "Smoke history", "metric": "improved"},
        ],
        "summary": {
            "card_count": 2,
            "current_ready": ready,
            "blocked_badge_count": blocked,
            "incomplete_badge_count": incomplete,
            "history_entry_count": 2,
            "ready_for_runtime_review": ready,
        },
    }


def sample_decision() -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_decision",
        "decision": "ready_for_manual_qt_smoke",
        "recommended_next_step": "Manual Qt smoke attempt may be started by the user.",
        "requires_user_confirmation": True,
        "executes_immediately": False,
    }


def sample_history() -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_history",
        "entries": [
            {"active_page_id": "dashboard", "ready_for_release_gate": False, "problem_count": 1},
            {"active_page_id": "people-review", "ready_for_release_gate": True, "problem_count": 0},
            {"active_page_id": "people-review", "ready_for_release_gate": False, "problem_count": 2},
        ],
    }

from media_manager.core.gui_qt_runtime_smoke_workbench import build_qt_runtime_smoke_workbench
from media_manager.core.gui_qt_runtime_smoke_workbench_actions import build_qt_runtime_smoke_workbench_actions


def test_workbench_actions_keep_manual_qt_smoke_confirmation_only() -> None:
    workbench = build_qt_runtime_smoke_workbench(sample_dashboard(), sample_decision())
    actions = build_qt_runtime_smoke_workbench_actions(workbench)

    start = [item for item in actions["actions"] if item["id"] == "start-manual-qt-smoke"][0]

    assert actions["summary"]["action_count"] == 4
    assert actions["summary"]["confirmation_action_count"] == 1
    assert start["enabled"] is True
    assert start["requires_confirmation"] is True
    assert start["executes_immediately"] is False


def test_workbench_actions_add_blocked_review_action() -> None:
    workbench = build_qt_runtime_smoke_workbench(sample_dashboard(ready=False, blocked=1), {})
    actions = build_qt_runtime_smoke_workbench_actions(workbench)

    assert actions["summary"]["danger_action_count"] == 1
    assert any(item["id"] == "review-failed-smoke-checks" for item in actions["actions"])
