from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app import main as app_main
from media_manager.core.app_manifest import build_app_manifest, build_ui_state_from_report
from media_manager.core.run_artifacts import write_run_artifacts
from media_manager.core.run_index import build_run_artifacts_payload, list_run_artifacts, load_run_artifact_payload


def test_app_manifest_contains_gui_ready_commands() -> None:
    manifest = build_app_manifest()

    command_ids = {item["id"] for item in manifest["commands"]}

    assert {"organize", "rename", "duplicates", "cleanup", "doctor", "runs"}.issubset(command_ids)
    assert manifest["artifact_contract"]["ui_state_file"] == "ui_state.json"
    assert "video" in manifest["media_formats"]
    assert "audio" in manifest["media_formats"]


def test_build_ui_state_from_report_exposes_overview_and_review() -> None:
    report = {
        "outcome_report": {
            "status": "review_required",
            "safe_to_apply": False,
            "needs_review": True,
            "blocked_count": 1,
            "actionable_count": 2,
            "next_action": "Review conflicts before applying.",
        },
        "review": {
            "candidate_count": 1,
            "reason_summary": {"conflict": 1},
            "candidates": [
                {
                    "section": "organize",
                    "source_path": "C:/in/a.jpg",
                    "target_path": "D:/out/a.jpg",
                    "status": "conflict",
                    "reason": "target exists",
                    "review_reasons": ["conflict"],
                }
            ],
        },
        "summary": {"planned_count": 2, "conflict_count": 1},
    }

    state = build_ui_state_from_report(command_name="organize", report_payload=report, run_id="run-1")

    assert state["overview"]["status"] == "review_required"
    assert state["overview"]["review_candidate_count"] == 1
    assert state["review"]["preview"][0]["source_path"] == "C:/in/a.jpg"
    assert state["sections"][0]["id"] == "summary"


def test_run_artifacts_write_ui_state(tmp_path: Path) -> None:
    payload = {
        "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False, "next_action": "Apply when ready."},
        "review": {"candidate_count": 0, "reason_summary": {}},
        "summary": {"planned_count": 1},
    }

    paths = write_run_artifacts(
        tmp_path,
        command_name="organize",
        argv=["organize", "--json"],
        apply_requested=False,
        exit_code=0,
        payload=payload,
        created_at_utc="2026-04-25T12:00:00Z",
    )

    ui_state_path = Path(paths["ui_state_path"])
    assert ui_state_path.is_file()
    ui_state = json.loads(ui_state_path.read_text(encoding="utf-8"))
    assert ui_state["command"] == "organize"
    assert ui_state["overview"]["status"] == "ready"

    records = list_run_artifacts(tmp_path)
    assert records[0].has_ui_state is True
    assert build_run_artifacts_payload(records, root_dir=tmp_path)["runs"][0]["has_ui_state"] is True
    assert load_run_artifact_payload(records[0].run_dir, "ui_state.json")["command"] == "organize"


def test_cli_app_manifest_json(capsys) -> None:
    exit_code = app_main(["manifest", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["application"]["id"] == "media-manager"
