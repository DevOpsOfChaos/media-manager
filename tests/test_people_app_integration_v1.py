from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app import main as app_main
from media_manager.core.action_model import build_action_model_from_report
from media_manager.core.app_manifest import build_app_manifest, build_ui_state_from_report
from media_manager.core.app_profiles import (
    build_app_profile_payload,
    render_app_profile_command,
    validate_app_profile,
)


def _people_report() -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "ok",
        "backend": "dlib",
        "backend_available": True,
        "strong_backend_available": True,
        "capabilities": {
            "face_detection": True,
            "named_person_matching": True,
            "unknown_face_grouping": True,
        },
        "summary": {
            "scanned_files": 2,
            "image_files": 2,
            "processed_files": 2,
            "face_count": 3,
            "matched_faces": 1,
            "unknown_faces": 2,
            "unknown_cluster_count": 1,
            "catalog_person_count": 1,
            "error_count": 0,
        },
        "detections": [
            {
                "path": "photos/a.jpg",
                "face_index": 0,
                "box": {"top": 1, "right": 10, "bottom": 11, "left": 2},
                "backend": "dlib",
                "matched_person_id": None,
                "matched_name": None,
                "unknown_cluster_id": "unknown-1",
                "encoding": [0.1, 0.2, 0.3],
            }
        ],
        "next_action": "Review detected faces.",
    }


def test_app_manifest_lists_people_as_first_class_command() -> None:
    manifest = build_app_manifest()
    command_ids = {command["id"] for command in manifest["commands"]}

    assert "people" in command_ids
    assert manifest["entrypoints"]["people"] == "media-manager people"
    assert manifest["entrypoints"]["people_session"] == "media-manager-people-session"
    assert "people_review_bundle_files" in manifest["artifact_contract"]
    assert "People review" in manifest["ui_guidance"]["recommended_primary_views"]


def test_people_ui_state_from_report_exposes_people_overview() -> None:
    state = build_ui_state_from_report(command_name="people", report_payload=_people_report())

    assert state["command"] == "people"
    assert state["mode"] == "review"
    assert state["overview"]["review_candidate_count"] == 2
    assert state["overview"]["people"]["unknown_faces"] == 2
    assert any(action["id"] == "review_people" and action["enabled"] for action in state["suggested_actions"])


def test_people_action_model_recommends_review_bundle() -> None:
    action_model = build_action_model_from_report(
        command_name="people",
        report_payload=_people_report(),
        command_payload={"argv": ["scan", "--source", "photos", "--report-json", "people-report.json", "--catalog", "people.json"]},
    )

    assert action_model["command_label"] == "Review people"
    assert action_model["next_action_id"] in {"people_review_bundle", "people_review_export"}
    actions = {action["id"]: action for action in action_model["actions"]}
    assert actions["people_review_bundle"]["enabled"] is True
    assert actions["people_review_apply"]["enabled"] is True


def test_people_app_profile_renders_scan_and_bundle_commands() -> None:
    scan_profile = build_app_profile_payload(
        profile_id="people-scan",
        title="People scan",
        command="people",
        values={"source_dirs": ["D:/Photos"], "catalog": "people.json", "backend": "dlib", "include_encodings": True},
    )
    validation = validate_app_profile(scan_profile)

    assert validation.valid is True
    assert validation.warnings
    assert render_app_profile_command(scan_profile) == "media-manager people scan --source D:/Photos --catalog people.json --backend dlib --include-encodings"

    bundle_profile = build_app_profile_payload(
        profile_id="people-bundle",
        title="People bundle",
        command="people",
        values={"people_mode": "review-bundle", "report_json": "people-report.json", "workflow_json": "people-workflow.json", "bundle_dir": "people-bundle", "catalog": "people.json"},
    )
    assert validate_app_profile(bundle_profile).valid is True
    assert render_app_profile_command(bundle_profile) == "media-manager people review-bundle --report-json people-report.json --workflow-json people-workflow.json --bundle-dir people-bundle --catalog people.json"


def test_cli_app_profiles_init_accepts_people(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "people-profile.json"

    assert app_main([
        "profiles",
        "init",
        "--out",
        str(profile_path),
        "--command",
        "people",
        "--title",
        "People scan",
        "--source",
        "D:/Photos",
        "--catalog",
        "people.json",
        "--backend",
        "dlib",
        "--include-encodings",
    ]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["valid"] is True
    assert payload["command"] == "people"
    assert profile_path.exists()
