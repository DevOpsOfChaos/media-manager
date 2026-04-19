from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    WorkflowHistoryEntry,
    build_history_summary_by_command,
    summarize_history_entries_by_command,
)


def _entry(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    record_type: str = "run_log",
    apply_requested: bool = False,
    exit_code: int = 0,
    entry_count: int = 1,
    reversible_entry_count: int = 0,
) -> WorkflowHistoryEntry:
    return WorkflowHistoryEntry(
        path=path,
        record_type=record_type,
        command_name=command_name,
        apply_requested=apply_requested,
        exit_code=exit_code,
        created_at_utc=created_at_utc,
        entry_count=entry_count,
        reversible_entry_count=reversible_entry_count,
    )


def _write_run_log(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    apply_requested: bool = False,
    exit_code: int = 0,
    entry_count: int = 1,
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": command_name,
                "apply_requested": apply_requested,
                "exit_code": exit_code,
                "created_at_utc": created_at_utc,
                "payload": {"entries": [{"status": "planned"} for _ in range(entry_count)]},
            }
        ),
        encoding="utf-8",
    )


def _write_execution_journal(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    apply_requested: bool = True,
    exit_code: int = 0,
    entry_count: int = 1,
    reversible_entry_count: int = 0,
) -> None:
    path.write_text(
        json.dumps(
            {
                "journal_type": "execution_journal",
                "command_name": command_name,
                "apply_requested": apply_requested,
                "exit_code": exit_code,
                "created_at_utc": created_at_utc,
                "entry_count": entry_count,
                "reversible_entry_count": reversible_entry_count,
            }
        ),
        encoding="utf-8",
    )


def test_summarize_history_entries_by_command_aggregates_counts_and_latest() -> None:
    entries = [
        _entry(Path("runs/rename-old.json"), command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00", exit_code=2, entry_count=2),
        _entry(Path("runs/rename-new.json"), command_name="rename", created_at_utc="2026-04-18T12:00:00+00:00", apply_requested=True, exit_code=0, entry_count=5),
        _entry(Path("runs/trip.json"), command_name="trip", created_at_utc="2026-04-18T11:00:00+00:00", record_type="execution_journal", apply_requested=True, exit_code=0, entry_count=3, reversible_entry_count=2),
    ]

    rows = summarize_history_entries_by_command(entries)

    assert [item.command_name for item in rows] == ["rename", "trip"]
    rename = rows[0]
    assert rename.entry_count == 2
    assert rename.successful_count == 1
    assert rename.failed_count == 1
    assert rename.apply_requested_count == 1
    assert rename.preview_only_count == 1
    assert rename.latest_created_at_utc == "2026-04-18T12:00:00+00:00"
    assert rename.latest_path.endswith("rename-new.json")
    assert rename.exit_code_summary == {"0": 1, "2": 1}

    trip = rows[1]
    assert trip.record_type_summary == {"execution_journal": 1}
    assert trip.reversible_entry_count == 2
    assert trip.entries_with_reversible_count == 1


def test_build_history_summary_by_command_reads_directory_and_respects_filters(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    _write_run_log(runs / "rename-preview.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00", apply_requested=False, exit_code=0, entry_count=2)
    _write_execution_journal(
        runs / "rename-apply.json",
        command_name="rename",
        created_at_utc="2026-04-18T12:00:00+00:00",
        apply_requested=True,
        exit_code=0,
        entry_count=4,
        reversible_entry_count=2,
    )
    _write_run_log(runs / "trip-failed.json", command_name="trip", created_at_utc="2026-04-18T11:00:00+00:00", apply_requested=True, exit_code=3, entry_count=5)

    rows = build_history_summary_by_command(
        runs,
        only_apply_requested=True,
        created_at_after="2026-04-18T11:30:00+00:00",
    )

    assert [item.command_name for item in rows] == ["rename"]
    assert rows[0].latest_path.endswith("rename-apply.json")
    assert rows[0].entry_count == 1
    assert rows[0].apply_requested_count == 1


def test_build_history_summary_by_command_can_focus_on_failed_commands(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    _write_run_log(runs / "rename-ok.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00", exit_code=0)
    _write_run_log(runs / "trip-failed.json", command_name="trip", created_at_utc="2026-04-18T11:00:00+00:00", exit_code=5)
    _write_execution_journal(
        runs / "duplicates-failed.json",
        command_name="duplicates",
        created_at_utc="2026-04-18T12:00:00+00:00",
        exit_code=7,
        reversible_entry_count=3,
    )

    rows = build_history_summary_by_command(runs, only_failed=True)

    assert [item.command_name for item in rows] == ["duplicates", "trip"]
    assert rows[0].latest_exit_code == 7
    assert rows[1].latest_exit_code == 5


def test_build_history_summary_by_command_returns_empty_list_for_empty_directory(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()

    rows = build_history_summary_by_command(runs)

    assert rows == []
