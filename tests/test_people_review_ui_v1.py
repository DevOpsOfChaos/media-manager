from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_people import main as people_main
from media_manager.core.people_review_ui import build_people_review_workspace
from media_manager.core.people_review_workflow import build_people_review_workflow


def _scan_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
        "capabilities": {
            "face_detection": True,
            "named_person_matching": True,
            "unknown_face_grouping": True,
        },
        "summary": {"face_count": 3, "unknown_faces": 2, "matched_faces": 1},
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
            {
                "path": "photos/c.jpg",
                "face_index": 0,
                "box": {"top": 9, "right": 10, "bottom": 11, "left": 12},
                "backend": "dlib",
                "matched_person_id": "person-jane",
                "matched_name": "Jane",
                "match_distance": 0.2,
                "unknown_cluster_id": None,
                "encoding": [0.9, 0.8, 0.7],
            },
        ],
    }


def test_people_review_workspace_builds_gui_cards_from_report() -> None:
    workspace = build_people_review_workspace(report_payload=_scan_report())

    assert workspace["workspace"] == "people_review_workspace"
    assert workspace["page_id"] == "people-review"
    assert workspace["overview"]["group_count"] == 2
    assert workspace["overview"]["face_count"] == 3
    assert workspace["overview"]["has_report_encodings"] is True

    unknown_group = next(group for group in workspace["groups"] if group["group_id"] == "unknown-1")
    assert unknown_group["status"] == "needs_review"
    assert unknown_group["counts"]["face_count"] == 2
    assert unknown_group["faces"][0]["decision_status"] == "pending_review"
    assert unknown_group["faces"][0]["image_uri"] == {"type": "local_path", "value": "photos/a.jpg"}


def test_people_review_workspace_reflects_curated_decisions() -> None:
    report = _scan_report()
    workflow = build_people_review_workflow(report)
    unknown_group = next(group for group in workflow["groups"] if group["review_group_id"] == "unknown-1")
    unknown_group["apply_group"] = True
    unknown_group["selected_name"] = "Max Example"
    unknown_group["faces"][1]["include"] = False

    workspace = build_people_review_workspace(report_payload=report, workflow_payload=workflow)

    group = next(group for group in workspace["groups"] if group["group_id"] == "unknown-1")
    assert group["status"] == "ready_to_apply"
    assert group["display_label"] == "Max Example"
    assert group["counts"]["included_faces"] == 1
    assert group["counts"]["excluded_faces"] == 1
    assert {face["decision_status"] for face in group["faces"]} == {"accepted", "rejected"}
    assert workspace["overview"]["ready_group_count"] == 1


def test_people_cli_review_state_writes_workspace_json(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "report.json"
    workflow_path = tmp_path / "workflow.json"
    workspace_path = tmp_path / "workspace.json"

    report = _scan_report()
    workflow = build_people_review_workflow(report)
    unknown_group = next(group for group in workflow["groups"] if group["review_group_id"] == "unknown-1")
    unknown_group["apply_group"] = True
    unknown_group["selected_name"] = "Max Example"

    report_path.write_text(json.dumps(report), encoding="utf-8")
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

    assert people_main([
        "review-state",
        "--report-json",
        str(report_path),
        "--workflow-json",
        str(workflow_path),
        "--out",
        str(workspace_path),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overview"]["ready_group_count"] == 1
    assert workspace_path.exists()
    written = json.loads(workspace_path.read_text(encoding="utf-8"))
    assert written["workspace"] == "people_review_workspace"
