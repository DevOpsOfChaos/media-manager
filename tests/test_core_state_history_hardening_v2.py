from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import WorkflowHistoryEntry, build_history_summary


def test_build_history_summary_counts_commands_and_outcomes() -> None:
    entries = [
        WorkflowHistoryEntry(
            path=Path("one.json"),
            record_type="run_log",
            command_name="rename",
            apply_requested=False,
            exit_code=0,
            created_at_utc="2026-04-18T10:00:00+00:00",
            entry_count=2,
            reversible_entry_count=0,
        ),
        WorkflowHistoryEntry(
            path=Path("two.json"),
            record_type="execution_journal",
            command_name="organize",
            apply_requested=True,
            exit_code=1,
            created_at_utc="2026-04-18T11:00:00+00:00",
            entry_count=3,
            reversible_entry_count=2,
        ),
    ]

    summary = build_history_summary(entries)

    assert summary["entry_count"] == 2
    assert summary["successful_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["reversible_entry_count"] == 2
    assert summary["command_summary"] == {"organize": 1, "rename": 1}
    assert summary["record_type_summary"] == {"execution_journal": 1, "run_log": 1}
    assert summary["apply_summary"] == {"apply_requested": 1, "preview_only": 1}
    assert summary["exit_code_summary"] == {"0": 1, "1": 1}
    assert summary["latest_created_at_utc"] == "2026-04-18T10:00:00+00:00"
