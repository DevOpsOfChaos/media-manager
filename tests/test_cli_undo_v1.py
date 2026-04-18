from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_undo import main
from media_manager.core.state import write_execution_journal


def test_cli_undo_json_preview_contains_summary(tmp_path: Path, capsys) -> None:
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
            }
        ],
    )

    exit_code = main(["--journal", str(journal), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["journal_command_name"] == "trip"
    assert payload["planned_count"] == 1
    assert payload["entries"][0]["status"] == "planned"


def test_cli_undo_apply_restores_rename_back(tmp_path: Path, capsys) -> None:
    original = tmp_path / "old.jpg"
    renamed = tmp_path / "new.jpg"
    renamed.write_bytes(b"jpg")
    journal = tmp_path / "journal.json"
    write_execution_journal(
        journal,
        command_name="rename",
        apply_requested=True,
        exit_code=0,
        entries=[
            {
                "source_path": str(original),
                "target_path": str(renamed),
                "outcome": "renamed",
                "reason": "done",
                "reversible": True,
                "undo_action": "rename_back",
                "undo_from_path": str(renamed),
                "undo_to_path": str(original),
            }
        ],
    )

    exit_code = main(["--journal", str(journal), "--json", "--apply"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["undone_count"] == 1
    assert payload["entries"][0]["status"] == "undone"
    assert original.exists()
    assert not renamed.exists()
