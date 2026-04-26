from pathlib import Path

from media_manager.core.gui_review_persistence import build_review_persistence_manifest, load_review_workspace_state, save_review_workspace_state


def test_build_review_persistence_manifest_lists_available_files() -> None:
    manifest = build_review_persistence_manifest(snapshot_path="snapshot.json", audit_log_path=None)
    assert manifest["available_files"] == ["snapshot"]
    assert manifest["safe_to_load"] is True


def test_save_and_load_review_workspace_state(tmp_path: Path) -> None:
    manifest = save_review_workspace_state(
        root_dir=tmp_path,
        snapshot={"kind": "gui_workspace_snapshot"},
        audit_log={"event_count": 1},
        selection_state={"selected_group_id": "g1"},
    )
    loaded = load_review_workspace_state(manifest["manifest_path"])
    assert loaded["snapshot"]["kind"] == "gui_workspace_snapshot"
    assert loaded["audit_log"]["event_count"] == 1
    assert loaded["selection"]["selected_group_id"] == "g1"
