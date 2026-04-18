from __future__ import annotations

from media_manager.core.state.execution_journal import build_execution_journal
from media_manager.core.state.run_log import build_command_run_log


def test_build_command_run_log_adds_payload_summary() -> None:
    payload = {
        "media_file_count": 5,
        "planned_count": 2,
        "skipped_count": 1,
        "conflict_count": 1,
        "error_count": 1,
        "execution": {
            "processed_count": 2,
            "executed_count": 1,
            "error_count": 1,
        },
    }

    result = build_command_run_log(
        command_name="organize",
        apply_requested=True,
        exit_code=1,
        payload=payload,
    )

    assert result["log_type"] == "command_run_log"
    assert result["payload_summary"]["media_file_count"] == 5
    assert result["payload_summary"]["execution"]["executed_count"] == 1


def test_build_execution_journal_adds_outcome_and_reason_summaries() -> None:
    entries = [
        {"outcome": "renamed", "reason": "rename applied successfully", "reversible": True},
        {"outcome": "conflict", "reason": "target exists", "reversible": False},
        {"outcome": "conflict", "reason": "target exists", "reversible": False},
    ]

    result = build_execution_journal(
        command_name="rename",
        apply_requested=True,
        exit_code=0,
        entries=entries,
    )

    assert result["entry_count"] == 3
    assert result["reversible_entry_count"] == 1
    assert result["outcome_summary"] == {"conflict": 2, "renamed": 1}
    assert result["reason_summary"] == {"rename applied successfully": 1, "target exists": 2}
