from __future__ import annotations

from pathlib import Path

from media_manager.core.people_recognition import PeopleCatalog, write_people_catalog
from media_manager.core.people_review_audit import build_people_review_apply_preview
from media_manager.core.people_review_workflow import build_people_review_workflow


def _scan_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
        "summary": {"face_count": 2, "unknown_faces": 2},
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


def test_people_review_apply_preview_reports_safe_to_apply(tmp_path: Path) -> None:
    catalog_path = tmp_path / "people.json"
    write_people_catalog(catalog_path, PeopleCatalog())
    report = _scan_report()
    workflow = build_people_review_workflow(report)
    group = workflow["groups"][0]
    group["apply_group"] = True
    group["selected_name"] = "Max Example"
    group["faces"][1]["include"] = False

    preview = build_people_review_apply_preview(
        catalog_path=catalog_path,
        workflow_payload=workflow,
        report_payload=report,
    )

    assert preview["kind"] == "people_review_apply_preview"
    assert preview["safe_to_apply"] is True
    assert preview["summary"]["ready_group_count"] == 1
    assert preview["summary"]["embeddings_added"] == 1
    assert preview["groups"][0]["included_face_count"] == 1
    assert preview["groups"][0]["rejected_face_count"] == 1


def test_people_review_apply_preview_blocks_missing_name(tmp_path: Path) -> None:
    catalog_path = tmp_path / "people.json"
    write_people_catalog(catalog_path, PeopleCatalog())
    report = _scan_report()
    workflow = build_people_review_workflow(report)
    workflow["groups"][0]["apply_group"] = True

    preview = build_people_review_apply_preview(
        catalog_path=catalog_path,
        workflow_payload=workflow,
        report_payload=report,
    )

    assert preview["safe_to_apply"] is False
    assert preview["summary"]["blocked_group_count"] == 1
    assert preview["groups"][0]["status"] == "blocked_missing_person"
