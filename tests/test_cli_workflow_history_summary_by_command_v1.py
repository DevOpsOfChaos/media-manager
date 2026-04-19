from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main
from media_manager.core.state import WorkflowHistoryEntry


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


def _entry(
    path: Path,
    *,
    command_name: str,
    record_type: str = "run_log",
    apply_requested: bool = False,
    exit_code: int = 0,
    created_at_utc: str = "2026-04-18T12:00:00+00:00",
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


def test_history_summary_by_command_json_returns_grouped_command_rows(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename-older.json", command_name="rename", created_at_utc="2026-04-18T09:00:00+00:00")
    _write_run_log(
        logs / "rename-newer.json",
        command_name="rename",
        created_at_utc="2026-04-18T10:00:00+00:00",
        apply_requested=True,
        entry_count=3,
    )
    _write_run_log(
        logs / "organize.json",
        command_name="organize",
        created_at_utc="2026-04-18T11:00:00+00:00",
        exit_code=2,
    )

    exit_code = main(["history-summary-by-command", "--path", str(logs), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["path"] == str(logs)
    assert payload["summary"]["entry_count"] == 3
    assert [item["command_name"] for item in payload["command_summaries"]] == ["organize", "rename"]
    assert payload["command_summaries"][0]["failed_count"] == 1
    assert payload["command_summaries"][1]["entry_count"] == 2
    assert payload["command_summaries"][1]["apply_requested_count"] == 1
    assert payload["command_summaries"][1]["preview_only_count"] == 1
    assert payload["command_summaries"][1]["latest_path"].endswith("rename-newer.json")



def test_history_summary_by_command_forwards_new_history_filters(monkeypatch, capsys, tmp_path: Path) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_scan(path: Path, **kwargs):
        captured_kwargs["path"] = path
        captured_kwargs.update(kwargs)
        return [
            _entry(
                tmp_path / "runs" / "trip-apply.json",
                command_name="trip",
                record_type="execution_journal",
                apply_requested=True,
                created_at_utc="2026-04-18T12:00:00+00:00",
                entry_count=9,
                reversible_entry_count=4,
            )
        ]

    monkeypatch.setattr("media_manager.cli_workflow.scan_history_directory", fake_scan)

    exit_code = main(
        [
            "history-summary-by-command",
            "--path",
            str(tmp_path / "runs"),
            "--record-type",
            "execution_journal",
            "--only-successful",
            "--only-apply",
            "--has-reversible-entries",
            "--min-entry-count",
            "4",
            "--min-reversible-entry-count",
            "1",
            "--created-at-after",
            "2026-04-01T00:00:00Z",
            "--created-at-before",
            "2026-04-30T23:59:59Z",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured_kwargs["path"] == tmp_path / "runs"
    assert captured_kwargs["record_type"] == "execution_journal"
    assert captured_kwargs["only_successful"] is True
    assert captured_kwargs["only_apply_requested"] is True
    assert captured_kwargs["has_reversible_entries"] is True
    assert captured_kwargs["min_entry_count"] == 4
    assert captured_kwargs["min_reversible_entry_count"] == 1
    assert captured_kwargs["created_at_after"] == "2026-04-01T00:00:00Z"
    assert captured_kwargs["created_at_before"] == "2026-04-30T23:59:59Z"

    payload = json.loads(captured.out)
    assert payload["record_type_filter"] == "execution_journal"
    assert payload["only_apply_requested"] is True
    assert payload["command_summaries"][0]["command_name"] == "trip"
    assert payload["command_summaries"][0]["entries_with_reversible_count"] == 1



def test_history_summary_by_command_summary_only_text_output(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00", exit_code=2)

    exit_code = main(["history-summary-by-command", "--path", str(logs), "--summary-only"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Workflow history summary by command" in captured.out
    assert "Commands matched: 2" in captured.out
    assert "Commands: organize=1, rename=1" in captured.out
    assert "rename | runs=" not in captured.out
    assert "rename.json" not in captured.out



def test_history_summary_by_command_fail_on_empty_returns_one(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()

    exit_code = main(["history-summary-by-command", "--path", str(logs), "--fail-on-empty"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No recognized run logs or execution journals found." in captured.out
