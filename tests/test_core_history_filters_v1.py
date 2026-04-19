from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    filter_history_entries,
    find_latest_history_entry,
    scan_history_directory,
    summarize_history_file,
)


def _write_run_log(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    apply_requested: bool,
    exit_code: int,
    entry_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": command_name,
                "apply_requested": apply_requested,
                "exit_code": exit_code,
                "created_at_utc": created_at_utc,
                "payload": {"entries": [{} for _ in range(entry_count)]},
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_execution_journal(
    path: Path,
    *,
    command_name: str,
    created_at_utc: str,
    apply_requested: bool,
    exit_code: int,
    entry_count: int,
    reversible_entry_count: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_filter_history_entries_supports_additive_audit_filters(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_run_log(
        root / "organize-preview.json",
        command_name="organize",
        created_at_utc="2026-04-18T09:00:00Z",
        apply_requested=False,
        exit_code=0,
        entry_count=4,
    )
    _write_execution_journal(
        root / "rename-apply.json",
        command_name="rename",
        created_at_utc="2026-04-18T10:00:00Z",
        apply_requested=True,
        exit_code=1,
        entry_count=6,
        reversible_entry_count=3,
    )
    _write_execution_journal(
        root / "organize-apply.json",
        command_name="organize",
        created_at_utc="2026-04-18T11:00:00Z",
        apply_requested=True,
        exit_code=0,
        entry_count=8,
        reversible_entry_count=2,
    )

    entries = scan_history_directory(root)
    filtered = filter_history_entries(
        entries,
        command_name="organize",
        only_successful=True,
        only_apply_requested=True,
        has_reversible_entries=True,
        min_entry_count=5,
        min_reversible_entry_count=2,
    )

    assert [item.path.name for item in filtered] == ["organize-apply.json"]


def test_scan_history_directory_applies_record_type_and_failure_filters(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_run_log(
        root / "duplicates-preview.json",
        command_name="duplicates",
        created_at_utc="2026-04-18T09:00:00Z",
        apply_requested=False,
        exit_code=2,
        entry_count=2,
    )
    _write_execution_journal(
        root / "duplicates-apply.json",
        command_name="duplicates",
        created_at_utc="2026-04-18T10:00:00Z",
        apply_requested=True,
        exit_code=0,
        entry_count=5,
        reversible_entry_count=4,
    )

    filtered = scan_history_directory(
        root,
        record_type="run_log",
        only_failed=True,
        only_preview=True,
    )

    assert [item.path.name for item in filtered] == ["duplicates-preview.json"]


def test_find_latest_history_entry_respects_new_filters(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    _write_execution_journal(
        root / "older-success.json",
        command_name="trip",
        created_at_utc="2026-04-18T08:00:00Z",
        apply_requested=True,
        exit_code=0,
        entry_count=4,
        reversible_entry_count=1,
    )
    _write_execution_journal(
        root / "newer-failed.json",
        command_name="trip",
        created_at_utc="2026-04-18T09:00:00Z",
        apply_requested=True,
        exit_code=1,
        entry_count=4,
        reversible_entry_count=1,
    )
    _write_execution_journal(
        root / "newest-success.json",
        command_name="trip",
        created_at_utc="2026-04-18T10:00:00Z",
        apply_requested=False,
        exit_code=0,
        entry_count=1,
        reversible_entry_count=0,
    )

    entry = find_latest_history_entry(
        root,
        command_name="trip",
        only_successful=True,
        only_apply_requested=True,
        has_reversible_entries=True,
    )

    assert entry is not None
    assert entry.path.name == "older-success.json"


def test_summarize_history_file_still_ignores_unrecognized_json(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps({"hello": "world"}), encoding="utf-8")

    assert summarize_history_file(path) is None
