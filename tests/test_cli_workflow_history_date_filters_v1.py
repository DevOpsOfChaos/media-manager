from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main
from media_manager.core.state.history import WorkflowHistoryEntry


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
    path: str | Path,
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


def test_history_json_filters_by_created_at_window(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "earlier.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "later.json", command_name="organize", created_at_utc="2026-04-19T11:00:00+00:00")

    exit_code = main([
        "history",
        "--path",
        str(logs),
        "--created-at-after",
        "2026-04-19T00:00:00Z",
        "--created-at-before",
        "2026-04-19T23:59:59Z",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["created_at_after"] == "2026-04-19T00:00:00Z"
    assert payload["created_at_before"] == "2026-04-19T23:59:59Z"
    assert [item["command_name"] for item in payload["entries"]] == ["organize"]


def test_history_text_prints_created_at_filter_labels(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_scan(path: Path, **kwargs):
        return []

    monkeypatch.setattr("media_manager.cli_workflow.scan_history_directory", fake_scan)

    exit_code = main([
        "history",
        "--path",
        str(tmp_path / "runs"),
        "--created-at-after",
        "2026-04-01T00:00:00Z",
        "--created-at-before",
        "2026-04-30T23:59:59Z",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Created at after: 2026-04-01T00:00:00Z" in captured.out
    assert "Created at before: 2026-04-30T23:59:59Z" in captured.out


def test_last_json_forwards_created_at_filters(monkeypatch, capsys, tmp_path: Path) -> None:
    captured_kwargs: dict[str, object] = {}

    def fake_last(path: Path, **kwargs):
        captured_kwargs["path"] = path
        captured_kwargs.update(kwargs)
        return _entry(
            tmp_path / "runs" / "trip-apply.json",
            command_name="trip",
            created_at_utc="2026-04-19T12:00:00Z",
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
        "--created-at-after",
        "2026-04-10T00:00:00Z",
        "--created-at-before",
        "2026-04-20T00:00:00Z",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured_kwargs["path"] == tmp_path / "runs"
    assert captured_kwargs["command_name"] == "trip"
    assert captured_kwargs["created_at_after"] == "2026-04-10T00:00:00Z"
    assert captured_kwargs["created_at_before"] == "2026-04-20T00:00:00Z"

    payload = json.loads(captured.out)
    assert payload["path"] == str(tmp_path / "runs")
    assert payload["created_at_after"] == "2026-04-10T00:00:00Z"
    assert payload["created_at_before"] == "2026-04-20T00:00:00Z"
    assert payload["entry"]["command_name"] == "trip"
    assert payload["command_name"] == "trip"


def test_last_text_prints_missing_entry_with_created_at_filter_context(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_last(path: Path, **kwargs):
        return None

    monkeypatch.setattr("media_manager.cli_workflow.find_latest_history_entry", fake_last)

    exit_code = main([
        "last",
        "--path",
        str(tmp_path / "runs"),
        "--created-at-after",
        "2026-04-01T00:00:00Z",
        "--created-at-before",
        "2026-04-30T23:59:59Z",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No recognized workflow history entry found." in captured.out
    assert "Created at after: 2026-04-01T00:00:00Z" in captured.out
    assert "Created at before: 2026-04-30T23:59:59Z" in captured.out
