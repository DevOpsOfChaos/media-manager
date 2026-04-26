from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.people_review_services import (
    build_people_review_service_state,
    load_people_review_bundle,
    rebuild_people_review_workspace_for_bundle,
    resolve_people_review_bundle_paths,
    split_people_review_group,
    update_people_review_face,
    update_people_review_group,
)
from media_manager.core.people_review_ui import build_people_review_workspace
from media_manager.core.people_review_workflow import build_people_review_workflow, write_people_review_workflow
from media_manager.core.report_export import write_json_report


def _scan_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
        "summary": {"face_count": 2, "unknown_faces": 2, "matched_faces": 0},
        "detections": [
            {
                "path": "photos/a.jpg",
                "face_index": 0,
                "box": {"top": 1, "right": 2, "bottom": 3, "left": 4},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.1, 0.2, 0.3],
            },
            {
                "path": "photos/b.jpg",
                "face_index": 0,
                "box": {"top": 5, "right": 6, "bottom": 7, "left": 8},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.11, 0.21, 0.31],
            },
        ],
    }


def _write_bundle(tmp_path: Path) -> Path:
    bundle_dir = tmp_path / "people-review-bundle"
    paths = resolve_people_review_bundle_paths(bundle_dir)
    report = _scan_report()
    workflow = build_people_review_workflow(report)
    workspace = build_people_review_workspace(report_payload=report, workflow_payload=workflow)
    write_json_report(paths.report_path, report)
    write_people_review_workflow(paths.workflow_path, workflow)
    write_json_report(paths.workspace_path, workspace)
    write_json_report(paths.manifest_path, {"kind": "people_review_bundle", "contains_sensitive_biometric_metadata": True})
    return bundle_dir


def test_load_people_review_bundle_builds_service_payload(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path)

    payload = load_people_review_bundle(bundle_dir)
    state = build_people_review_service_state(bundle_dir)

    assert payload["service"] == "people_review_service"
    assert payload["workflow"]["workflow"] == "people_review"
    assert state["summary"]["group_count"] == 1
    assert state["suggested_actions"][0]["id"] == "continue_review"


def test_service_updates_group_and_rebuilds_workspace(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path)

    result = update_people_review_group(
        bundle_dir,
        group_id="unknown-1",
        apply_group=True,
        selected_name="Max Example",
    )

    assert result["status"] == "ok"
    assert result["changed"] is True
    assert result["rebuild"]["status"] == "ok"
    workflow = json.loads((bundle_dir / "people_review_workflow.json").read_text(encoding="utf-8"))
    group = workflow["groups"][0]
    assert group["apply_group"] is True
    assert group["selected_name"] == "Max Example"
    workspace = json.loads((bundle_dir / "people_review_workspace.json").read_text(encoding="utf-8"))
    assert workspace["overview"]["ready_group_count"] == 1


def test_service_updates_face_decision_and_can_split_group(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path)
    workflow = json.loads((bundle_dir / "people_review_workflow.json").read_text(encoding="utf-8"))
    first_face_id = workflow["groups"][0]["faces"][0]["face_id"]

    face_result = update_people_review_face(bundle_dir, face_id=first_face_id, include=False, note="wrong person")
    assert face_result["status"] == "ok"
    assert face_result["changed"] is True

    split_result = split_people_review_group(
        bundle_dir,
        group_id="unknown-1",
        face_ids=[first_face_id],
        new_group_id="manual-other-person",
    )
    assert split_result["status"] == "ok"
    assert split_result["changed"] is True

    state = build_people_review_service_state(bundle_dir)
    assert state["summary"]["group_count"] == 2


def test_rebuild_people_review_workspace_for_bundle(tmp_path: Path) -> None:
    bundle_dir = _write_bundle(tmp_path)

    result = rebuild_people_review_workspace_for_bundle(bundle_dir)

    assert result["operation"] == "rebuild-workspace"
    assert result["status"] == "ok"
    assert (bundle_dir / "people_review_workspace.json").exists()
