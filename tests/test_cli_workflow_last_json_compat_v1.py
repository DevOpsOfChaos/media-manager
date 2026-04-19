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


def test_cli_workflow_last_json_output_keeps_backward_compatible_top_level_fields(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T10:00:00+00:00")
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00")

    exit_code = main(["last", "--path", str(logs), "--command", "rename", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["command_name"] == "rename"
    assert payload["command_filter"] == "rename"
    assert payload["record_type"] == "run_log"
