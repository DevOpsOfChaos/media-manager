from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    WorkflowHistoryEntry,
    find_latest_history_entries_by_command,
    latest_history_entries_by_command,
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
    entries = [{"status": "planned"} for _ in range(entry_count)]
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": command_name,
                "apply_requested": apply_requested,
                "exit_code": exit_code,
                "created_at_utc": created_at_utc,
                "payload": {"entries": entries},
            }
        ),
        encoding="utf-8",
    )


def _write_execution_journal(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    apply_requested: bool = False,
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


def _entry(
    path: str,
    *,
    command_name: str,
    created_at_utc: str,
    record_type: str = "run_log",
    exit_code: int = 0,
    apply_requested: bool = False,
    entry_count: int = 1,
    reversible_entry_count: int = 0,
) -> WorkflowHistoryEntry:
    return WorkflowHistoryEntry(
        path=Path(path),
        record_type=record_type,
        command_name=command_name,
        apply_requested=apply_requested,
        exit_code=exit_code,
        created_at_utc=created_at_utc,
        entry_count=entry_count,
        reversible_entry_count=reversible_entry_count,
    )


def test_latest_history_entries_by_command_keeps_newest_matching_entry_per_command() -> None:
    entries = [
        _entry("runs/rename-old.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00"),
        _entry("runs/organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00"),
        _entry("runs/rename-new.json", command_name="rename", created_at_utc="2026-04-18T12:00:00+00:00"),
        _entry("runs/trip.json", command_name="trip", created_at_utc="2026-04-18T09:00:00+00:00"),
    ]

    latest = latest_history_entries_by_command(entries)

    assert [item.command_name for item in latest] == ["rename", "organize", "trip"]
    assert [item.path.name for item in latest] == ["rename-new.json", "organize.json", "trip.json"]


def test_find_latest_history_entries_by_command_scans_directory_and_sorts_newest_first(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename-old.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "rename-new.json", command_name="rename", created_at_utc="2026-04-18T13:00:00+00:00")
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T12:00:00+00:00")
    _write_run_log(logs / "trip.json", command_name="trip", created_at_utc="2026-04-18T11:00:00+00:00")

    latest = find_latest_history_entries_by_command(logs)

    assert [item.command_name for item in latest] == ["rename", "organize", "trip"]
    assert [item.path.name for item in latest] == ["rename-new.json", "organize.json", "trip.json"]


def test_find_latest_history_entries_by_command_respects_failure_and_record_type_filters(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename-success.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00", exit_code=0)
    _write_run_log(logs / "rename-failed.json", command_name="rename", created_at_utc="2026-04-18T11:00:00+00:00", exit_code=2)
    _write_execution_journal(
        logs / "trip-journal.json",
        command_name="trip",
        created_at_utc="2026-04-18T12:00:00+00:00",
        exit_code=3,
        reversible_entry_count=2,
    )
    _write_execution_journal(
        logs / "organize-journal.json",
        command_name="organize",
        created_at_utc="2026-04-18T13:00:00+00:00",
        exit_code=0,
        reversible_entry_count=4,
    )

    latest_failed_journals = find_latest_history_entries_by_command(
        logs,
        only_failed=True,
        record_type="execution_journal",
    )

    assert [item.command_name for item in latest_failed_journals] == ["trip"]
    assert latest_failed_journals[0].path.name == "trip-journal.json"


def test_find_latest_history_entries_by_command_respects_date_windows_and_apply_mode(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(
        logs / "rename-preview-old.json",
        command_name="rename",
        created_at_utc="2026-04-17T08:00:00+00:00",
        apply_requested=False,
    )
    _write_run_log(
        logs / "rename-apply.json",
        command_name="rename",
        created_at_utc="2026-04-18T09:00:00+00:00",
        apply_requested=True,
    )
    _write_execution_journal(
        logs / "trip-apply-same-day.json",
        command_name="trip",
        created_at_utc="2026-04-18T10:00:00+00:00",
        apply_requested=True,
        reversible_entry_count=3,
    )
    _write_execution_journal(
        logs / "trip-apply-late.json",
        command_name="trip",
        created_at_utc="2026-04-19T10:00:00+00:00",
        apply_requested=True,
        reversible_entry_count=5,
    )

    latest = find_latest_history_entries_by_command(
        logs,
        only_apply_requested=True,
        created_at_after="2026-04-18T00:00:00+00:00",
        created_at_before="2026-04-18T23:59:59+00:00",
    )

    assert [item.command_name for item in latest] == ["trip", "rename"]
    assert [item.path.name for item in latest] == ["trip-apply-same-day.json", "rename-apply.json"]
