from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main
from media_manager.core.people_recognition import PeopleCatalog, write_people_catalog
from media_manager.core.people_review_workflow import build_people_review_workflow


def test_cli_app_services_pages_json(capsys) -> None:
    assert app_services_main(["pages", "--active-page", "people-review", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["navigation"]["active_page_id"] == "people-review"
    assert any(page["page_id"] == "people-review" for page in payload["catalog"]["pages"])


def test_cli_app_services_people_review_preview_json(tmp_path: Path, capsys) -> None:
    catalog_path = tmp_path / "people.json"
    report_path = tmp_path / "report.json"
    workflow_path = tmp_path / "workflow.json"
    write_people_catalog(catalog_path, PeopleCatalog())
    report = {
        "schema_version": 1,
        "detections": [
            {
                "path": "photos/a.jpg",
                "face_index": 0,
                "box": {"top": 1, "right": 2, "bottom": 3, "left": 4},
                "backend": "dlib",
                "matched_person_id": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.1, 0.2, 0.3],
            }
        ],
    }
    workflow = build_people_review_workflow(report)
    workflow["groups"][0]["apply_group"] = True
    workflow["groups"][0]["selected_name"] = "Max Example"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    workflow_path.write_text(json.dumps(workflow), encoding="utf-8")

    assert app_services_main([
        "people-review-preview",
        "--catalog",
        str(catalog_path),
        "--workflow-json",
        str(workflow_path),
        "--report-json",
        str(report_path),
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["safe_to_apply"] is True
