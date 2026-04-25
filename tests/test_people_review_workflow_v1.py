from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_people import main as people_main
from media_manager.core.people_recognition import load_people_catalog, write_people_catalog, PeopleCatalog
from media_manager.core.people_review_workflow import (
    apply_people_review_workflow,
    build_people_review_workflow,
)


def _scan_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
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
                "unknown_cluster_id": None,
                "encoding": [0.9, 0.8, 0.7],
            },
        ],
    }


def test_build_people_review_workflow_groups_unknown_and_matched_faces() -> None:
    workflow = build_people_review_workflow(_scan_report())

    assert workflow["workflow"] == "people_review"
    assert workflow["group_count"] == 2
    groups = {group["review_group_id"]: group for group in workflow["groups"]}

    assert groups["unknown-1"]["group_type"] == "unknown_cluster"
    assert len(groups["unknown-1"]["faces"]) == 2
    assert groups["unknown-1"]["apply_group"] is False

    assert groups["matched-person-jane"]["group_type"] == "matched_person"
    assert groups["matched-person-jane"]["selected_person_id"] == "person-jane"
    assert groups["matched-person-jane"]["selected_name"] == "Jane"


def test_apply_people_review_workflow_creates_person_and_skips_rejected_face(tmp_path: Path) -> None:
    catalog_path = tmp_path / "people.json"
    write_people_catalog(catalog_path, PeopleCatalog())

    report = _scan_report()
    workflow = build_people_review_workflow(report)
    unknown_group = next(group for group in workflow["groups"] if group["review_group_id"] == "unknown-1")
    unknown_group["apply_group"] = True
    unknown_group["selected_name"] = "Max Example"
    unknown_group["faces"][1]["include"] = False

    result = apply_people_review_workflow(
        catalog_path=catalog_path,
        workflow_payload=workflow,
        report_payload=report,
    )

    assert result.status == "ok"
    assert result.groups_applied == 1
    assert result.persons_created == 1
    assert result.embeddings_added == 1
    assert result.faces_rejected == 1

    catalog = load_people_catalog(catalog_path)
    person = next(iter(catalog.persons.values()))
    assert person.name == "Max Example"
    assert len(person.embeddings) == 1
    assert person.embeddings[0].source_path == "photos/a.jpg"


def test_apply_people_review_workflow_requires_encodings(tmp_path: Path) -> None:
    catalog_path = tmp_path / "people.json"
    write_people_catalog(catalog_path, PeopleCatalog())

    report = _scan_report()
    for detection in report["detections"]:
        detection.pop("encoding", None)

    workflow = build_people_review_workflow(report)
    unknown_group = next(group for group in workflow["groups"] if group["review_group_id"] == "unknown-1")
    unknown_group["apply_group"] = True
    unknown_group["selected_name"] = "Max Example"

    result = apply_people_review_workflow(
        catalog_path=catalog_path,
        workflow_payload=workflow,
        report_payload=report,
        dry_run=True,
    )

    assert result.status == "completed_with_problems"
    assert {problem["code"] for problem in result.problems} == {"missing_encoding"}


def test_people_cli_review_export_and_apply(tmp_path: Path, capsys) -> None:
    catalog_path = tmp_path / "people.json"
    report_path = tmp_path / "report.json"
    workflow_path = tmp_path / "workflow.json"

    report_path.write_text(json.dumps(_scan_report()), encoding="utf-8")

    assert people_main(["catalog-init", "--catalog", str(catalog_path)]) == 0
    capsys.readouterr()

    assert people_main(["review-export", "--report-json", str(report_path), "--out", str(workflow_path), "--json"]) == 0
    workflow = json.loads(capsys.readouterr().out)
    assert workflow["group_count"] == 2

    unknown_group = next(group for group in workflow["groups"] if group["review_group_id"] == "unknown-1")
    unknown_group["apply_group"] = True
    unknown_group["selected_name"] = "Max Example"
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

    assert people_main([
        "review-apply",
        "--catalog",
        str(catalog_path),
        "--workflow-json",
        str(workflow_path),
        "--report-json",
        str(report_path),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["persons_created"] == 1
    assert payload["summary"]["embeddings_added"] == 2
