from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main
from media_manager.core.state.history import WorkflowHistoryEntry


def _entry(
    path: str,
    *,
    record_type: str = "execution_journal",
    command_name: str = "organize",
    apply_requested: bool = True,
    exit_code: int = 0,
    created_at_utc: str = "2026-04-19T10:00:00Z",
    entry_count: int = 5,
    reversible_entry_count: int = 2,
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


def test_history_json_forwards_new_filters_and_supports_summary_only(monkeypatch, capsys, tmp_path: Path) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_scan(path: Path, **kwargs):
        captured_kwargs["path"] = path
        captured_kwargs.update(kwargs)
        return [_entry(tmp_path / "runs" / "organize.json")]

    monkeypatch.setattr("media_manager.cli_workflow.scan_history_directory", fake_scan)

    exit_code = main([
        "history",
        "--path",
        str(tmp_path / "runs"),
        "--command",
        "organize",
        "--record-type",
        "execution_journal",
        "--only-successful",
        "--only-apply",
        "--has-reversible-entries",
        "--min-entry-count",
        "5",
        "--min-reversible-entry-count",
        "2",
        "--summary-only",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured_kwargs["path"] == tmp_path / "runs"
    assert captured_kwargs["command_name"] == "organize"
    assert captured_kwargs["record_type"] == "execution_journal"
    assert captured_kwargs["only_successful"] is True
    assert captured_kwargs["only_failed"] is False
    assert captured_kwargs["only_apply_requested"] is True
    assert captured_kwargs["only_preview"] is False
    assert captured_kwargs["has_reversible_entries"] is True
    assert captured_kwargs["min_entry_count"] == 5
    assert captured_kwargs["min_reversible_entry_count"] == 2

    payload = json.loads(captured.out)
    assert payload["path"] == str(tmp_path / "runs")
    assert payload["command_filter"] == "organize"
    assert payload["record_type_filter"] == "execution_journal"
    assert payload["only_successful"] is True
    assert payload["only_apply_requested"] is True
    assert payload["has_reversible_entries"] is True
    assert payload["min_entry_count"] == 5
    assert payload["min_reversible_entry_count"] == 2
    assert payload["summary_only"] is True
    assert payload["summary"]["entry_count"] == 1
    assert payload["entries"] == []



def test_history_text_prints_filter_labels_and_fail_on_empty(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_scan(path: Path, **kwargs):
        return []

    monkeypatch.setattr("media_manager.cli_workflow.scan_history_directory", fake_scan)

    exit_code = main([
        "history",
        "--path",
        str(tmp_path / "runs"),
        "--record-type",
        "run_log",
        "--only-failed",
        "--only-preview",
        "--fail-on-empty",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Record type filter: run_log" in captured.out
    assert "Success filter: only failed" in captured.out
    assert "Mode filter: preview only" in captured.out
    assert "No recognized run logs or execution journals found." in captured.out



def test_last_json_forwards_new_filters(monkeypatch, capsys, tmp_path: Path) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_last(path: Path, **kwargs):
        captured_kwargs["path"] = path
        captured_kwargs.update(kwargs)
        return _entry(
            tmp_path / "runs" / "trip-apply.json",
            command_name="trip",
            entry_count=9,
            reversible_entry_count=4,
        )

    monkeypatch.setattr("media_manager.cli_workflow.find_latest_history_entry", fake_last)

    exit_code = main([
        "last",
        "--path",
        str(tmp_path / "runs"),
        "--command",
        "trip",
        "--record-type",
        "execution_journal",
        "--only-successful",
        "--has-reversible-entries",
        "--min-entry-count",
        "4",
        "--min-reversible-entry-count",
        "1",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured_kwargs["path"] == tmp_path / "runs"
    assert captured_kwargs["command_name"] == "trip"
    assert captured_kwargs["record_type"] == "execution_journal"
    assert captured_kwargs["only_successful"] is True
    assert captured_kwargs["has_reversible_entries"] is True
    assert captured_kwargs["min_entry_count"] == 4
    assert captured_kwargs["min_reversible_entry_count"] == 1

    payload = json.loads(captured.out)
    assert payload["path"] == str(tmp_path / "runs")
    assert payload["command_filter"] == "trip"
    assert payload["record_type_filter"] == "execution_journal"
    assert payload["entry"]["command_name"] == "trip"
    assert payload["entry"]["reversible_entry_count"] == 4



def test_last_text_reports_missing_entry_with_filter_context(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_last(path: Path, **kwargs):
        return None

    monkeypatch.setattr("media_manager.cli_workflow.find_latest_history_entry", fake_last)

    exit_code = main([
        "last",
        "--path",
        str(tmp_path / "runs"),
        "--command",
        "rename",
        "--only-successful",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No recognized workflow history entry found." in captured.out
    assert "Command filter: rename" in captured.out
    assert "Success filter: only successful" in captured.out
