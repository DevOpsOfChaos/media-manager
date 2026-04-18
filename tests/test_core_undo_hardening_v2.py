from __future__ import annotations

from pathlib import Path

from media_manager.core.state.undo import UndoEntryResult, UndoExecutionResult


def test_undo_execution_result_summary_properties_group_entries() -> None:
    result = UndoExecutionResult(
        apply_requested=False,
        journal_path=Path("journal.json"),
        journal_command_name="rename",
        original_apply_requested=True,
        original_exit_code=0,
        entries=[
            UndoEntryResult(undo_action="rename_back", source_path=Path("a"), target_path=Path("b"), status="planned", reason="would restore the original source path from the journal"),
            UndoEntryResult(undo_action="rename_back", source_path=Path("c"), target_path=Path("d"), status="planned", reason="would restore the original source path from the journal"),
            UndoEntryResult(undo_action=None, source_path=None, target_path=None, status="skipped", reason="journal entry is not reversible"),
        ],
    )

    assert result.ready_to_apply_count == 2
    assert result.status_summary == {"planned": 2, "skipped": 1}
    assert result.undo_action_summary == {"none": 1, "rename_back": 2}
    assert result.reason_summary == {
        "journal entry is not reversible": 1,
        "would restore the original source path from the journal": 2,
    }
