from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    WorkflowHistoryEntry,
    build_history_audit_snapshot,
    scan_history_audit_snapshot,
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


def _write_run_log(path: Path, *, command_name: str, created_at_utc: str, apply_requested: bool = False, exit_code: int = 0, entry_count: int = 1) -> None:
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


def _write_execution_journal(path: Path, *, command_name: str, created_at_utc: str, apply_requested: bool = False, exit_code: int = 0, entry_count: int = 1, reversible_entry_count: int = 0) -> None:
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


def test_build_history_audit_snapshot_from_entries_combines_summary_latest_and_command_rows() -> None:
    entries = [
        _entry(Path("runs/rename-old.json"), command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00", exit_code=2),
        _entry(Path("runs/rename-new.json"), command_name="rename", created_at_utc="2026-04-18T12:00:00+00:00", apply_requested=True, exit_code=0),
        _entry(Path("runs/trip.json"), command_name="trip", created_at_utc="2026-04-18T11:00:00+00:00", record_type="execution_journal", reversible_entry_count=3),
    ]

    snapshot = build_history_audit_snapshot(entries, path="runs", only_failed=False)

    assert snapshot.path == "runs"
    assert snapshot.summary["entry_count"] == 3
    assert [item.command_name for item in snapshot.latest_entries_by_command] == ["rename", "trip"]
    assert [item.command_name for item in snapshot.command_summaries] == ["rename", "trip"]
    payload = snapshot.to_dict()
    assert payload["path"] == "runs"
    assert payload["summary"]["entry_count"] == 3
    assert [item["command_name"] for item in payload["latest_entries_by_command"]] == ["rename", "trip"]
    assert [item["command_name"] for item in payload["command_summaries"]] == ["rename", "trip"]


def test_scan_history_audit_snapshot_reads_directory_and_respects_filters(tmp_path: Path) -> None:
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

    snapshot = scan_history_audit_snapshot(
        runs,
        only_apply_requested=True,
        created_at_after="2026-04-18T11:30:00+00:00",
    )

    assert snapshot.path == str(runs)
    assert snapshot.only_apply_requested is True
    assert snapshot.created_at_after == "2026-04-18T11:30:00+00:00"
    assert [item.command_name for item in snapshot.latest_entries_by_command] == ["rename"]
    assert [item.command_name for item in snapshot.command_summaries] == ["rename"]
    assert snapshot.summary["entry_count"] == 1


def test_scan_history_audit_snapshot_keeps_empty_sections_for_empty_directory(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()

    snapshot = scan_history_audit_snapshot(runs)

    assert snapshot.summary["entry_count"] == 0
    assert snapshot.latest_entries_by_command == []
    assert snapshot.command_summaries == []
