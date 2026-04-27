from __future__ import annotations


def sample_page_model(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_page_model",
        "page_id": "runtime-smoke",
        "title": "Runtime Smoke",
        "subtitle": "Review Qt runtime readiness before opening a window.",
        "active_page_id": "people-review",
        "presenter": {
            "title": "Runtime Smoke",
            "subtitle": "Review Qt runtime readiness before opening a window.",
            "status": "ready" if ready else "blocked",
            "severity": "success" if ready else "error",
            "metrics": {
                "section_count": 3,
                "card_count": 2,
                "badge_count": 2,
                "history_entry_count": 2,
                "ready_for_runtime_review": ready,
                "requires_user_confirmation": True,
            },
        },
        "table": {
            "columns": ["title", "metric", "problem_count", "privacy_check_count", "artifact_count", "ready"],
            "rows": [
                {"row_id": "current-report", "title": "Current runtime smoke", "metric": "ready" if ready else "blocked", "problem_count": 0 if ready else 1, "privacy_check_count": 2, "artifact_count": 0, "ready": ready},
                {"row_id": "artifacts", "title": "Local artifacts", "metric": 2, "problem_count": 0, "privacy_check_count": 0, "artifact_count": 2, "ready": False},
            ],
            "summary": {
                "row_count": 2,
                "ready_row_count": 1 if ready else 0,
                "problem_count_total": 0 if ready else 1,
                "privacy_check_count_total": 2,
                "artifact_count_total": 2,
            },
        },
        "detail": {
            "status": "ready" if ready else "blocked",
            "recommended_next_step": "Manual Qt smoke attempt may be started by the user.",
            "privacy": {
                "local_only": True,
                "network_required": False,
                "telemetry_allowed": False,
                "contains_sensitive_people_data_possible": True,
            },
        },
        "actions": [
            {"id": "refresh-runtime-smoke", "label": "Refresh smoke data", "enabled": True},
            {"id": "start-manual-qt-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True},
        ],
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }

from media_manager.core.gui_qt_runtime_smoke_visible_plan import build_qt_runtime_smoke_visible_plan


def test_visible_plan_builds_four_visible_sections() -> None:
    plan = build_qt_runtime_smoke_visible_plan(sample_page_model())

    assert plan["kind"] == "qt_runtime_smoke_visible_plan"
    assert plan["page_id"] == "runtime-smoke"
    assert plan["summary"]["section_count"] == 4
    assert plan["summary"]["row_count"] == 2
    assert plan["summary"]["action_count"] == 2
    assert plan["summary"]["ready_for_runtime_review"] is True
    assert plan["summary"]["contains_sensitive_people_data_possible"] is True
    assert plan["capabilities"]["opens_window"] is False


def test_visible_plan_preserves_blocked_state() -> None:
    plan = build_qt_runtime_smoke_visible_plan(sample_page_model(ready=False))
    status = plan["sections"][0]

    assert status["component"] == "StatusBanner"
    assert status["props"]["severity"] == "error"
    assert plan["summary"]["ready_for_runtime_review"] is False
