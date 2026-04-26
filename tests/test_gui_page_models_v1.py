from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.gui_page_models import (
    build_dashboard_page_model,
    build_page_model,
    build_profiles_page_model,
    build_runs_page_model,
    load_people_review_page_model,
)


def _home_state(tmp_path: Path) -> dict[str, object]:
    return {
        "suggested_next_step": "Open people review.",
        "profiles": {
            "summary": {"profile_count": 1, "valid_count": 1, "favorite_count": 1},
            "items": [
                {"path": str(tmp_path / "profile.json"), "profile_id": "p1", "title": "Main", "command": "people", "favorite": True, "valid": True}
            ],
        },
        "runs": {
            "summary": {"run_count": 1, "error_count": 0},
            "items": [
                {"path": str(tmp_path / "run1"), "run_id": "run1", "command": "people", "mode": "preview", "status": "ok", "exit_code": 0}
            ],
        },
        "people_review": {"bundle_dir": str(tmp_path / "bundle"), "ready_for_gui": True, "summary": {"group_count": 2, "face_count": 4}},
        "manifest_summary": {"schema_version": "1.0", "command_count": 7, "entrypoints": {"people": "media-manager people"}},
    }


def test_dashboard_page_model_summarizes_home_state(tmp_path: Path) -> None:
    page = build_dashboard_page_model(_home_state(tmp_path))

    assert page["page_id"] == "dashboard"
    assert page["kind"] == "dashboard_page"
    assert len(page["cards"]) == 3
    assert page["cards"][2]["metrics"]["ready_for_gui"] is True


def test_runs_and_profiles_page_models_build_rows(tmp_path: Path) -> None:
    home = _home_state(tmp_path)

    runs = build_runs_page_model(home)
    profiles = build_profiles_page_model(home)

    assert runs["rows"][0]["run_id"] == "run1"
    assert profiles["rows"][0]["profile_id"] == "p1"


def test_people_review_page_model_loads_bundle_files(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    (bundle / "assets" / "faces").mkdir(parents=True)
    crop = bundle / "assets" / "faces" / "face-1.jpg"
    crop.write_bytes(b"data")
    (bundle / "bundle_manifest.json").write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    (bundle / "people_review_workspace.json").write_text(
        json.dumps(
            {
                "overview": {"group_count": 1, "face_count": 1},
                "groups": [
                    {
                        "group_id": "unknown-1",
                        "display_label": "unknown-1",
                        "status": "needs_review",
                        "primary_face_id": "face-1",
                        "counts": {"face_count": 1, "included_faces": 1, "excluded_faces": 0},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "assets" / "people_review_assets.json").write_text(
        json.dumps({"assets": [{"face_id": "face-1", "asset_path": str(crop), "status": "ok"}]}),
        encoding="utf-8",
    )

    page = load_people_review_page_model(bundle)

    assert page["page_id"] == "people-review"
    assert page["group_count"] == 1
    assert page["asset_refs"][0]["face_id"] == "face-1"


def test_build_page_model_returns_placeholder_for_unknown_page(tmp_path: Path) -> None:
    page = build_page_model("future-page", _home_state(tmp_path))

    assert page["kind"] == "placeholder_page"
