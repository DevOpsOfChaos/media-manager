from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from media_manager.core.people_review_bundle_validator import validate_people_review_bundle


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_validate_people_review_bundle_reports_ready_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    asset_dir = bundle / "assets" / "faces"
    asset_dir.mkdir(parents=True)
    crop = asset_dir / "face-1.jpg"
    Image.new("RGB", (12, 12)).save(crop)
    _write_json(bundle / "bundle_manifest.json", {"status": "ok", "summary": {"ready_group_count": 1}})
    _write_json(bundle / "people_report.json", {"schema_version": 1})
    _write_json(bundle / "people_review_workflow.json", {"workflow": "people_review"})
    _write_json(bundle / "people_review_workspace.json", {"workspace": "people_review_workspace"})
    (bundle / "summary.txt").write_text("summary", encoding="utf-8")
    _write_json(bundle / "assets" / "people_review_assets.json", {"assets": [{"status": "ok", "asset_path": str(crop)}]})

    result = validate_people_review_bundle(bundle)

    assert result["status"] == "ok"
    assert result["ready_for_gui"] is True
    assert result["summary"]["asset_count"] == 1
    assert result["diagnostics"] == []


def test_validate_people_review_bundle_reports_missing_required_files(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_json(bundle / "bundle_manifest.json", {"status": "ok"})

    result = validate_people_review_bundle(bundle)

    assert result["status"] == "error"
    assert result["ready_for_gui"] is False
    codes = {item["code"] for item in result["diagnostics"]}
    assert "required_file_missing" in codes
