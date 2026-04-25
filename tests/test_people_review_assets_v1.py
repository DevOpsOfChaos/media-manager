from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from media_manager.cli_people import main as people_main
from media_manager.core.people_review_assets import build_people_review_assets, face_id_for_detection


def _write_image(path: Path) -> None:
    image = Image.new("RGB", (100, 80), color=(120, 120, 120))
    image.save(path)


def _report(image_path: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
        "summary": {"face_count": 1, "unknown_faces": 1, "matched_faces": 0},
        "detections": [
            {
                "path": str(image_path),
                "face_index": 0,
                "box": {"top": 20, "right": 70, "bottom": 60, "left": 30},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.1, 0.2, 0.3],
            }
        ],
    }


def test_build_people_review_assets_writes_face_crop(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    _write_image(image_path)
    asset_dir = tmp_path / "assets"

    payload = build_people_review_assets(report_payload=_report(image_path), asset_dir=asset_dir, thumbnail_size=32)

    assert payload["kind"] == "people_review_assets"
    assert payload["summary"]["generated_count"] == 1
    assert payload["summary"]["error_count"] == 0
    asset = payload["assets"][0]
    assert asset["status"] == "ok"
    assert Path(asset["asset_path"]).exists()
    with Image.open(asset["asset_path"]) as cropped:
        assert cropped.width <= 32
        assert cropped.height <= 32


def test_build_people_review_assets_reports_missing_source(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jpg"

    payload = build_people_review_assets(report_payload=_report(missing), asset_dir=tmp_path / "assets")

    assert payload["summary"]["generated_count"] == 0
    assert payload["summary"]["error_count"] == 1
    assert payload["assets"][0]["error"] == "source_image_missing"


def test_people_review_assets_respects_workflow_face_subset(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"
    _write_image(image_path)
    report = _report(image_path)
    detection = report["detections"][0]
    face_id = face_id_for_detection(detection["path"], detection["face_index"])
    workflow = {
        "groups": [
            {
                "review_group_id": "unknown-1",
                "group_type": "unknown_cluster",
                "apply_group": True,
                "selected_name": "Jane Example",
                "faces": [{"face_id": face_id, "path": str(image_path), "face_index": 0, "include": False}],
            }
        ]
    }

    payload = build_people_review_assets(report_payload=report, workflow_payload=workflow, asset_dir=tmp_path / "assets")

    assert payload["summary"]["asset_count"] == 1
    assert payload["assets"][0]["review_group_id"] == "unknown-1"
    assert payload["assets"][0]["include"] is False
    assert payload["assets"][0]["selected_name"] == "Jane Example"


def test_people_cli_review_assets_writes_manifest(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "photo.jpg"
    _write_image(image_path)
    report_path = tmp_path / "report.json"
    asset_dir = tmp_path / "assets"
    manifest_path = tmp_path / "manifest.json"
    report_path.write_text(json.dumps(_report(image_path)), encoding="utf-8")

    assert people_main([
        "review-assets",
        "--report-json",
        str(report_path),
        "--asset-dir",
        str(asset_dir),
        "--out",
        str(manifest_path),
        "--thumbnail-size",
        "32",
        "--json",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert manifest_path.exists()
    assert payload["summary"]["generated_count"] == 1
    assert Path(payload["assets"][0]["asset_path"]).exists()
