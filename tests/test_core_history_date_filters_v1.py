from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    WorkflowHistoryEntry,
    filter_history_entries,
    find_latest_history_entry,
    scan_history_directory,
)


def _entry(
    path: str,
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
        path=Path(path),
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
    payload = {
        "schema_version": 1,
        "command_name": command_name,
        "apply_requested": apply_requested,
        "exit_code": exit_code,
        "created_at_utc": created_at_utc,
        "payload": {"entries": [{"status": "planned"} for _ in range(entry_count)]},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_filter_history_entries_supports_created_at_after_and_before() -> None:
    entries = [
        _entry("logs/one.json", command_name="rename", created_at_utc="2026-04-10T10:00:00+00:00"),
        _entry("logs/two.json", command_name="rename", created_at_utc="2026-04-15T10:00:00+00:00"),
        _entry("logs/three.json", command_name="rename", created_at_utc="2026-04-20T10:00:00+00:00"),
    ]

    filtered = filter_history_entries(
        entries,
        created_at_after="2026-04-12T00:00:00+00:00",
        created_at_before="2026-04-18T00:00:00+00:00",
    )

    assert [item.path.name for item in filtered] == ["two.json"]


def test_filter_history_entries_excludes_invalid_timestamps_when_date_window_is_used() -> None:
    entries = [
        _entry("logs/good.json", command_name="rename", created_at_utc="2026-04-15T10:00:00+00:00"),
        _entry("logs/bad.json", command_name="rename", created_at_utc="not-a-timestamp"),
    ]

    filtered = filter_history_entries(entries, created_at_after="2026-04-01T00:00:00+00:00")

    assert [item.path.name for item in filtered] == ["good.json"]


def test_scan_history_directory_applies_date_window_filters(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename-old.json", command_name="rename", created_at_utc="2026-04-10T10:00:00+00:00")
    _write_run_log(logs / "rename-window.json", command_name="rename", created_at_utc="2026-04-15T10:00:00+00:00")
    _write_run_log(logs / "organize-new.json", command_name="organize", created_at_utc="2026-04-20T10:00:00+00:00")

    entries = scan_history_directory(
        logs,
        created_at_after="2026-04-12T00:00:00+00:00",
        created_at_before="2026-04-18T00:00:00+00:00",
    )

    assert [item.path.name for item in entries] == ["rename-window.json"]


def test_find_latest_history_entry_respects_date_window_and_other_filters(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "trip-preview.json", command_name="trip", created_at_utc="2026-04-12T10:00:00+00:00", apply_requested=False)
    _write_run_log(logs / "trip-apply.json", command_name="trip", created_at_utc="2026-04-14T10:00:00+00:00", apply_requested=True)
    _write_run_log(logs / "trip-late.json", command_name="trip", created_at_utc="2026-04-20T10:00:00+00:00", apply_requested=True)

    entry = find_latest_history_entry(
        logs,
        command_name="trip",
        only_apply_requested=True,
        created_at_before="2026-04-18T00:00:00+00:00",
    )

    assert entry is not None
    assert entry.path.name == "trip-apply.json"
