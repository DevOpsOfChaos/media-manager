from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_people_session import main as session_main
from media_manager.core.people_review_session import (
    build_people_review_session_state,
    merge_people_groups,
    set_people_face_decision,
    set_people_group_decision,
    split_people_group,
    summarize_people_review_workflow,
)


def _workflow() -> dict[str, object]:
    return {
        "schema_version": 1,
        "workflow": "people_review",
        "review_status": "needs_user_review",
        "groups": [
            {
                "review_group_id": "unknown-1",
                "group_type": "unknown_cluster",
                "apply_group": False,
                "selected_person_id": "",
                "selected_name": "",
                "faces": [
                    {"face_id": "face-a", "path": "a.jpg", "face_index": 0, "include": True},
                    {"face_id": "face-b", "path": "b.jpg", "face_index": 0, "include": True},
                ],
            },
            {
                "review_group_id": "unknown-2",
                "group_type": "unknown_cluster",
                "apply_group": False,
                "selected_person_id": "",
                "selected_name": "",
                "faces": [
                    {"face_id": "face-c", "path": "c.jpg", "face_index": 0, "include": True},
                ],
            },
        ],
    }


def test_group_and_face_decisions_prepare_ready_group() -> None:
    workflow = _workflow()

    group_result = set_people_group_decision(
        workflow,
        group_id="unknown-1",
        apply_group=True,
        selected_name="Max Example",
        review_note="looks consistent",
    )
    face_result = set_people_face_decision(group_result.workflow_payload, face_id="face-b", include=False, note="wrong person")

    summary = summarize_people_review_workflow(face_result.workflow_payload)

    assert group_result.status == "ok"
    assert face_result.status == "ok"
    assert summary["ready_group_count"] == 1
    assert summary["included_faces"] == 2
    assert summary["rejected_faces"] == 1
    group = face_result.workflow_payload["groups"][0]
    assert group["selected_name"] == "Max Example"
    assert group["faces"][1]["include"] is False


def test_split_group_moves_selected_faces_to_new_manual_group() -> None:
    result = split_people_group(_workflow(), group_id="unknown-1", face_ids=["face-b"], new_group_id="manual-other")

    assert result.status == "ok"
    assert result.changed is True
    groups = {group["review_group_id"]: group for group in result.workflow_payload["groups"]}
    assert len(groups["unknown-1"]["faces"]) == 1
    assert groups["manual-other"]["group_type"] == "manual_split"
    assert groups["manual-other"]["faces"][0]["face_id"] == "face-b"


def test_merge_groups_combines_faces_and_removes_sources() -> None:
    result = merge_people_groups(
        _workflow(),
        group_ids=["unknown-1", "unknown-2"],
        target_group_id="manual-merged",
        selected_name="Same Person",
    )

    assert result.status == "ok"
    assert result.changed is True
    assert len(result.workflow_payload["groups"]) == 1
    merged = result.workflow_payload["groups"][0]
    assert merged["review_group_id"] == "manual-merged"
    assert merged["group_type"] == "manual_merge"
    assert merged["selected_name"] == "Same Person"
    assert len(merged["faces"]) == 3


def test_session_state_suggests_apply_when_group_is_ready() -> None:
    workflow = _workflow()
    result = set_people_group_decision(workflow, group_id="unknown-1", apply_group=True, selected_name="Max Example")
    state = build_people_review_session_state(result.workflow_payload)

    assert state["session"] == "people_review_session"
    assert state["summary"]["ready_group_count"] == 1
    action = next(item for item in state["suggested_actions"] if item["id"] == "apply_ready_groups")
    assert action["enabled"] is True


def test_people_session_cli_edits_workflow_json(tmp_path: Path, capsys) -> None:
    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(json.dumps(_workflow()), encoding="utf-8")

    assert session_main([
        "group-set",
        "--workflow-json",
        str(workflow_path),
        "--group-id",
        "unknown-1",
        "--apply",
        "--selected-name",
        "Max Example",
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["ready_group_count"] == 1

    assert session_main([
        "face-set",
        "--workflow-json",
        str(workflow_path),
        "--face-id",
        "face-b",
        "--exclude",
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["rejected_faces"] == 1

    saved = json.loads(workflow_path.read_text(encoding="utf-8"))
    assert saved["groups"][0]["selected_name"] == "Max Example"
    assert saved["groups"][0]["faces"][1]["include"] is False
