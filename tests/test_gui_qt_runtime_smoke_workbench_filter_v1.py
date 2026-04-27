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

from media_manager.core.gui_qt_runtime_smoke_workbench_filter import filter_qt_runtime_smoke_history


def test_workbench_filter_limits_history_by_page_and_ready_state() -> None:
    result = filter_qt_runtime_smoke_history(sample_history(), active_page_id="people-review", ready=False)

    assert result["summary"]["entry_count"] == 1
    assert result["summary"]["not_ready_count"] == 1
    assert result["summary"]["problem_count_total"] == 2


def test_workbench_filter_applies_limit_from_tail() -> None:
    result = filter_qt_runtime_smoke_history(sample_history(), limit=2)

    assert result["summary"]["entry_count"] == 2
    assert result["entries"][0]["active_page_id"] == "people-review"
