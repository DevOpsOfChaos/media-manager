
from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state.history import (
    build_history_summary,
    find_latest_history_entry,
    scan_history_directory,
    summarize_history_file,
)


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


def test_build_history_summary_keeps_legacy_and_extended_fields(tmp_path: Path) -> None:
    (tmp_path / "preview.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": "rename",
                "apply_requested": False,
                "exit_code": 0,
                "created_at_utc": "2026-04-18T09:00:00+00:00",
                "payload": {"entries": [{"status": "planned"}]},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "apply.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "journal_type": "execution_journal",
                "command_name": "organize",
                "apply_requested": True,
                "exit_code": 2,
                "created_at_utc": "2026-04-18T11:00:00+00:00",
                "entry_count": 2,
                "reversible_entry_count": 1,
                "entries": [],
            }
        ),
        encoding="utf-8",
    )

    entries = scan_history_directory(tmp_path)
    summary = build_history_summary(entries)

    assert summary["entry_count"] == 2
    assert summary["total_entries"] == 2
    assert summary["command_summary"] == {"organize": 1, "rename": 1}
    assert summary["command_name_summary"] == {"organize": 1, "rename": 1}
    assert summary["apply_summary"] == {"apply_requested": 1, "preview_only": 1}
    assert summary["exit_code_summary"] == {"0": 1, "2": 1}
    assert summary["entries_with_reversible_count"] == 1
