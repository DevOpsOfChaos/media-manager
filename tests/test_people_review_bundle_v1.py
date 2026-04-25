from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from media_manager.cli_people import main as people_main
from media_manager.core.people_review_bundle import BUNDLE_KIND, write_people_review_bundle


def _write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (120, 100), color=(120, 120, 120))
    image.save(path)


def _scan_report(image_path: Path) -> dict[str, object]:
    return {
        "schema_version": 1,
        "backend": "dlib",
        "capabilities": {"face_detection": True, "named_person_matching": True, "unknown_face_grouping": True},
        "summary": {"face_count": 2, "unknown_faces": 2, "matched_faces": 0},
        "detections": [
            {
                "path": str(image_path),
                "face_index": 0,
                "box": {"top": 20, "right": 70, "bottom": 80, "left": 20},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.1, 0.2, 0.3],
            },
            {
                "path": str(image_path),
                "face_index": 1,
                "box": {"top": 10, "right": 105, "bottom": 55, "left": 65},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.11, 0.21, 0.31],
            },
        ],
    }


def test_write_people_review_bundle_creates_gui_artifacts_and_assets(tmp_path: Path) -> None:
    image_path = tmp_path / "photos" / "family.jpg"
    _write_image(image_path)
    bundle_dir = tmp_path / "bundle"

    manifest = write_people_review_bundle(report_payload=_scan_report(image_path), bundle_dir=bundle_dir)

    assert manifest["kind"] == BUNDLE_KIND
    assert manifest["files"]["manifest"] == "bundle_manifest.json"
    assert manifest["files"]["workspace"] == "people_review_workspace.json"
    assert manifest["files"]["workflow"] == "people_review_workflow.json"
    assert manifest["files"]["assets"] == "assets/people_review_assets.json"
    assert manifest["summary"]["asset_count"] == 2
    assert manifest["summary"]["asset_error_count"] == 0
    assert manifest["contains_sensitive_biometric_metadata"] is True

    assert (bundle_dir / "bundle_manifest.json").exists()
    assert (bundle_dir / "people_report.json").exists()
    assert (bundle_dir / "people_review_workflow.json").exists()
    assert (bundle_dir / "people_review_workspace.json").exists()
    assert (bundle_dir / "assets" / "people_review_assets.json").exists()
    assert (bundle_dir / "summary.txt").read_text(encoding="utf-8").startswith("People review bundle")

    workspace = json.loads((bundle_dir / "people_review_workspace.json").read_text(encoding="utf-8"))
    face = workspace["groups"][0]["faces"][0]
    assert face["asset_status"] == "ok"
    assert face["asset_relative_path"].startswith("assets/faces/face-")
    assert face["asset_uri"]["type"] == "local_path"
    assert workspace["overview"]["has_face_assets"] is True


def test_write_people_review_bundle_can_skip_assets(tmp_path: Path) -> None:
    image_path = tmp_path / "photos" / "family.jpg"
    _write_image(image_path)
    bundle_dir = tmp_path / "bundle"

    manifest = write_people_review_bundle(
        report_payload=_scan_report(image_path),
        bundle_dir=bundle_dir,
        include_assets=False,
    )

    assert manifest["files"]["assets"] is None
    assert manifest["summary"]["asset_count"] == 0
    assert (bundle_dir / "people_review_workspace.json").exists()
    assert not (bundle_dir / "assets" / "people_review_assets.json").exists()


def test_people_cli_review_bundle_writes_manifest(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "photos" / "family.jpg"
    _write_image(image_path)
    report_path = tmp_path / "people-report.json"
    bundle_dir = tmp_path / "bundle"
    report_path.write_text(json.dumps(_scan_report(image_path)), encoding="utf-8")

    exit_code = people_main([
        "review-bundle",
        "--report-json",
        str(report_path),
        "--bundle-dir",
        str(bundle_dir),
        "--json",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "people_review_bundle"
    assert payload["summary"]["asset_count"] == 2
    assert (bundle_dir / "bundle_manifest.json").exists()


def test_people_cli_review_bundle_text_output(tmp_path: Path, capsys) -> None:
    image_path = tmp_path / "photos" / "family.jpg"
    _write_image(image_path)
    report_path = tmp_path / "people-report.json"
    bundle_dir = tmp_path / "bundle"
    report_path.write_text(json.dumps(_scan_report(image_path)), encoding="utf-8")

    exit_code = people_main([
        "review-bundle",
        "--report-json",
        str(report_path),
        "--bundle-dir",
        str(bundle_dir),
        "--no-assets",
    ])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "People review bundle" in output
    assert "Workspace:" in output
