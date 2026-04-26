from pathlib import Path

from media_manager.core.gui_qt_pending_changes import build_pending_change
from media_manager.core.gui_qt_save_state import build_workspace_save_state, read_workspace_save_state, write_workspace_save_state
from media_manager.core.gui_qt_undo_redo_stack import build_undo_redo_stack, push_undo, redo_once, undo_once


def test_undo_redo_roundtrip() -> None:
    stack = build_undo_redo_stack()
    stack = push_undo(stack, build_pending_change("rename_group", target_id="g1"))
    assert stack["can_undo"] is True
    stack = undo_once(stack)
    assert stack["can_redo"] is True
    stack = redo_once(stack)
    assert stack["can_undo"] is True
    assert stack["redo_count"] == 0


def test_save_state_can_be_written_and_loaded(tmp_path: Path) -> None:
    state = build_workspace_save_state(workspace_path=tmp_path / "workflow.json", pending_change_count=2)
    assert state["has_unsaved_changes"] is True
    path = write_workspace_save_state(tmp_path / "state.json", state)
    loaded = read_workspace_save_state(path)
    assert loaded["pending_change_count"] == 2
    assert loaded["saved_at_utc"].endswith("Z")
