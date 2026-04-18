from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state import build_execution_journal, load_execution_journal, write_execution_journal


def test_build_execution_journal_counts_reversible_entries() -> None:
    payload = build_execution_journal(
        command_name="organize",
        apply_requested=True,
        exit_code=0,
        entries=[
            {"outcome": "copied", "reversible": True},
            {"outcome": "skipped", "reversible": False},
        ],
    )

    assert payload["schema_version"] == 1
    assert payload["journal_type"] == "execution_journal"
    assert payload["command_name"] == "organize"
    assert payload["apply_requested"] is True
    assert payload["exit_code"] == 0
    assert payload["entry_count"] == 2
    assert payload["reversible_entry_count"] == 1


def test_write_and_load_execution_journal_roundtrip(tmp_path: Path) -> None:
    journal_path = tmp_path / "journals" / "organize-execution.json"
    written_path = write_execution_journal(
        journal_path,
        command_name="rename",
        apply_requested=True,
        exit_code=0,
        entries=[
            {
                "source_path": str(tmp_path / "old.jpg"),
                "target_path": str(tmp_path / "new.jpg"),
                "outcome": "renamed",
                "reason": "rename applied successfully",
                "reversible": True,
                "undo_action": "rename_back",
                "undo_from_path": str(tmp_path / "new.jpg"),
                "undo_to_path": str(tmp_path / "old.jpg"),
            }
        ],
    )

    assert written_path == journal_path
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "rename"
    assert payload["entry_count"] == 1
    assert payload["entries"][0]["undo_action"] == "rename_back"

    loaded = load_execution_journal(journal_path)
    assert loaded["command_name"] == "rename"
    assert loaded["entries"][0]["undo_action"] == "rename_back"
