from __future__ import annotations


def sample_workbench(*, status: str = "ready", ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_workbench",
        "language": "en",
        "active_page_id": "people-review",
        "status": status,
        "message": "Ready for manual runtime review" if ready else "Resolve failed runtime smoke checks",
        "recommended_next_step": "Manual Qt smoke attempt may be started by the user.",
        "decision": {
            "decision": "ready_for_manual_qt_smoke" if ready else "blocked",
            "severity": "success" if ready else "error",
            "requires_user_confirmation": True,
            "executes_immediately": False,
        },
        "sections": [
            {
                "id": "runtime-smoke-status",
                "title": "Runtime smoke status",
                "kind": "status_strip",
                "items": [{"state": status}, {"state": "ready"}],
            },
            {
                "id": "runtime-smoke-cards",
                "title": "Runtime smoke metrics",
                "kind": "metric_cards",
                "items": [
                    {
                        "id": "current-report",
                        "title": "Current runtime smoke",
                        "metric": "ready" if ready else "blocked",
                        "details": {
                            "check_count": 4,
                            "result_count": 4,
                            "problem_count": 0 if ready else 1,
                            "privacy_check_count": 2,
                        },
                    },
                    {
                        "id": "artifacts",
                        "title": "Local artifacts",
                        "metric": 2,
                        "details": {
                            "artifact_count": 2,
                            "metadata_only_count": 2,
                            "sensitive_media_count": 0,
                            "all_local_only": True,
                        },
                    },
                ],
            },
            {
                "id": "runtime-smoke-trend",
                "title": "Runtime smoke trend",
                "kind": "trend",
                "items": [{"ready": False}, {"ready": True}],
                "summary": {
                    "entry_count": 2,
                    "direction": "improved",
                    "latest_ready": ready,
                    "latest_active_page_id": "people-review",
                },
            },
        ],
        "summary": {
            "section_count": 3,
            "card_count": 2,
            "badge_count": 2,
            "history_entry_count": 2,
            "ready_for_runtime_review": ready,
            "requires_user_confirmation": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def sample_actions() -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_workbench_actions",
        "actions": [
            {"id": "refresh-runtime-smoke", "label": "Refresh smoke data", "enabled": True},
            {"id": "start-manual-qt-smoke", "label": "Start manual Qt smoke", "enabled": True, "requires_confirmation": True},
        ],
        "summary": {"action_count": 2},
    }

from media_manager.core.gui_qt_runtime_smoke_table_model import build_qt_runtime_smoke_table_model


def test_runtime_smoke_table_model_turns_cards_into_rows() -> None:
    table = build_qt_runtime_smoke_table_model(sample_workbench())

    assert table["kind"] == "qt_runtime_smoke_table_model"
    assert table["summary"]["row_count"] == 2
    assert table["summary"]["ready_row_count"] == 1
    assert table["summary"]["privacy_check_count_total"] == 2
    assert table["summary"]["artifact_count_total"] == 2
    assert "problem_count" in table["columns"]


def test_runtime_smoke_table_model_keeps_blocked_problem_count() -> None:
    table = build_qt_runtime_smoke_table_model(sample_workbench(status="blocked", ready=False))

    assert table["summary"]["problem_count_total"] == 1
    assert table["rows"][0]["ready"] is False
