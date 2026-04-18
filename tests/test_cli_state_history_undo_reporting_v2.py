from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_undo import main as undo_main
from media_manager.cli_workflow import main as workflow_main
from media_manager.core.state import write_execution_journal


def _write_run_log(path: Path, *, command_name: str, created_at_utc: str, exit_code: int = 0, apply_requested: bool = False) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "command_name": command_name,
                "apply_requested": apply_requested,
                "exit_code": exit_code,
                "created_at_utc": created_at_utc,
                "payload": {"entries": [{"status": "planned"}]},
            }
        ),
        encoding="utf-8",
    )


def test_cli_workflow_history_json_includes_summary(tmp_path: Path, capsys) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _write_run_log(logs / "rename.json", command_name="rename", created_at_utc="2026-04-18T12:00:00+00:00", exit_code=0)
    _write_run_log(logs / "organize.json", command_name="organize", created_at_utc="2026-04-18T11:00:00+00:00", exit_code=1, apply_requested=True)

    exit_code = workflow_main(["history", "--path", str(logs), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["entry_count"] == 2
    assert payload["summary"]["successful_count"] == 1
    assert payload["summary"]["failed_count"] == 1
    assert payload["summary"]["command_summary"] == {"organize": 1, "rename": 1}


def test_cli_undo_json_includes_summary_blocks(tmp_path: Path, capsys) -> None:
    target = tmp_path / "target.jpg"
    target.write_bytes(b"jpg")
    journal = tmp_path / "journal.json"
    write_execution_journal(
        journal,
        command_name="trip",
        apply_requested=True,
        exit_code=0,
        entries=[
            {
                "source_path": str(tmp_path / "source.jpg"),
                "target_path": str(target),
                "outcome": "copied",
                "reason": "done",
                "reversible": True,
                "undo_action": "delete_target",
                "undo_from_path": str(target),
                "undo_to_path": None,
            },
            {
                "source_path": str(tmp_path / "skip.jpg"),
                "target_path": None,
                "outcome": "skipped",
                "reason": "skip",
                "reversible": False,
                "undo_action": None,
                "undo_from_path": None,
                "undo_to_path": None,
            },
        ],
    )

    exit_code = undo_main(["--journal", str(journal), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["ready_to_apply_count"] == 1
    assert payload["status_summary"] == {"planned": 1, "skipped": 1}
    assert payload["undo_action_summary"] == {"delete_target": 1, "none": 1}
