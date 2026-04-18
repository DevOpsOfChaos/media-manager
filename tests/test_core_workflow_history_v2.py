from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import find_latest_history_entry, scan_history_directory, summarize_history_file


def test_summarize_history_file_supports_run_logs(tmp_path: Path) -> None:
    file_path = tmp_path / "rename-run.json"
    file_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": "rename",
                "apply_requested": False,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T12:00:00+00:00",
                "payload": {"entries": [{"status": "planned"}, {"status": "planned"}]},
            }
        ),
        encoding="utf-8",
    )

    summary = summarize_history_file(file_path)

    assert summary is not None
    assert summary.record_type == "run_log"
    assert summary.command_name == "rename"
    assert summary.entry_count == 2
    assert summary.reversible_entry_count == 0


def test_scan_history_directory_sorts_newest_first_and_filters_unknown_files(tmp_path: Path) -> None:
    (tmp_path / "ignore.json").write_text(json.dumps({"hello": "world"}), encoding="utf-8")
    (tmp_path / "older-run.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": "organize",
                "apply_requested": False,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T10:00:00+00:00",
                "payload": {"entries": []},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "newer-journal.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "journal_type": "execution_journal",
                "command_name": "trip",
                "apply_requested": True,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T11:00:00+00:00",
                "entry_count": 3,
                "reversible_entry_count": 2,
                "entries": [],
            }
        ),
        encoding="utf-8",
    )

    entries = scan_history_directory(tmp_path)

    assert [item.command_name for item in entries] == ["trip", "organize"]
    assert entries[0].record_type == "execution_journal"
    assert entries[0].reversible_entry_count == 2


def test_find_latest_history_entry_can_filter_by_command(tmp_path: Path) -> None:
    (tmp_path / "one.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": "rename",
                "apply_requested": False,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T09:00:00+00:00",
                "payload": {"entries": []},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "two.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": "organize",
                "apply_requested": True,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T11:00:00+00:00",
                "payload": {"entries": []},
            }
        ),
        encoding="utf-8",
    )

    latest = find_latest_history_entry(tmp_path, command_name="rename")

    assert latest is not None
    assert latest.command_name == "rename"
