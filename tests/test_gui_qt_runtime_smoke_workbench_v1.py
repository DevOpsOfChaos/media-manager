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

from media_manager.core.gui_qt_runtime_smoke_workbench import build_qt_runtime_smoke_workbench, summarize_qt_runtime_smoke_workbench


def test_smoke_workbench_builds_sections_from_dashboard_and_decision() -> None:
    workbench = build_qt_runtime_smoke_workbench(sample_dashboard(), sample_decision(), language="de")

    assert workbench["kind"] == "qt_runtime_smoke_workbench"
    assert workbench["language"] == "de"
    assert workbench["status"] == "ready"
    assert workbench["summary"]["section_count"] == 3
    assert workbench["summary"]["card_count"] == 2
    assert workbench["summary"]["ready_for_runtime_review"] is True
    assert workbench["capabilities"]["opens_window"] is False
    assert "Status: ready" in summarize_qt_runtime_smoke_workbench(workbench)


def test_smoke_workbench_marks_blocked_dashboard() -> None:
    workbench = build_qt_runtime_smoke_workbench(sample_dashboard(ready=False, blocked=1), {})

    assert workbench["status"] == "blocked"
    assert workbench["summary"]["ready_for_runtime_review"] is False
