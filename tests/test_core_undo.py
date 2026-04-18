from __future__ import annotations

from pathlib import Path

from media_manager.core.state import execute_undo_journal, write_execution_journal


def test_execute_undo_journal_previews_delete_target(tmp_path: Path) -> None:
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

    result = execute_undo_journal(journal, apply=False)

    assert result.entry_count == 1
    assert result.reversible_entry_count == 1
    assert result.planned_count == 1
    assert result.undone_count == 0
    assert target.exists()
    assert result.entries[0].status == "planned"


def test_execute_undo_journal_applies_move_back(tmp_path: Path) -> None:
    original = tmp_path / "original.jpg"
    moved = tmp_path / "moved.jpg"
    moved.write_bytes(b"jpg")
    journal = tmp_path / "journal.json"
    write_execution_journal(
        journal,
        command_name="organize",
        apply_requested=True,
        exit_code=0,
        entries=[
            {
                "source_path": str(original),
                "target_path": str(moved),
                "outcome": "moved",
                "reason": "done",
                "reversible": True,
                "undo_action": "move_back",
                "undo_from_path": str(moved),
                "undo_to_path": str(original),
            }
        ],
    )

    result = execute_undo_journal(journal, apply=True)

    assert result.undone_count == 1
    assert original.exists()
    assert not moved.exists()
    assert result.entries[0].status == "undone"


def test_execute_undo_journal_skips_non_reversible_entries(tmp_path: Path) -> None:
    journal = tmp_path / "journal.json"
    write_execution_journal(
        journal,
        command_name="rename",
        apply_requested=True,
        exit_code=0,
        entries=[
            {
                "source_path": str(tmp_path / "a.jpg"),
                "target_path": str(tmp_path / "b.jpg"),
                "outcome": "skipped",
                "reason": "already fine",
                "reversible": False,
                "undo_action": None,
                "undo_from_path": None,
                "undo_to_path": None,
            }
        ],
    )

    result = execute_undo_journal(journal, apply=True)

    assert result.skipped_count == 1
    assert result.entries[0].reason == "journal entry is not reversible"
