
from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main


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


def test_cli_workflow_history_json_output(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T12:00:00+00:00")

    exit_code = main(["history", "--path", str(logs), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["entries"][0]["command_name"] == "rename"
    assert payload["summary"]["entry_count"] == 1
    assert payload["command_filter"] is None


def test_cli_workflow_history_json_output_can_filter_by_command(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00")

    exit_code = main(["history", "--path", str(logs), "--command", "rename", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["command_filter"] == "rename"
    assert [item["command_name"] for item in payload["entries"]] == ["rename"]
    assert payload["summary"]["command_summary"] == {"rename": 1}


def test_cli_workflow_history_text_output_includes_apply_and_exit_summaries(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(
        logs / "rename.json",
        command_name="rename",
        created_at_utc="2026-04-18T10:00:00+00:00",
        apply_requested=False,
        exit_code=0,
        entry_count=2,
    )
    _write_run_log(
        logs / "organize.json",
        command_name="organize",
        created_at_utc="2026-04-18T11:00:00+00:00",
        apply_requested=True,
        exit_code=2,
        entry_count=1,
    )

    exit_code = main(["history", "--path", str(logs)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Apply modes: apply_requested=1, preview_only=1" in captured.out
    assert "Exit codes: 0=1, 2=1" in captured.out


def test_cli_workflow_last_json_output_filters_by_command(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00")

    exit_code = main(["last", "--path", str(logs), "--command", "rename", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["command_name"] == "rename"


def test_cli_workflow_last_returns_one_when_no_match(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00")

    exit_code = main(["last", "--path", str(logs), "--command", "rename"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "No recognized workflow history entry found" in captured.out
