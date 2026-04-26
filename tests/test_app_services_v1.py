from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.app_services import (
    build_app_home_state,
    build_report_service_bundle,
    discover_run_summaries,
    load_people_review_bundle_summary,
    write_report_service_bundle,
)


def _report_payload() -> dict[str, object]:
    return {
        "outcome_report": {
            "status": "ready",
            "safe_to_apply": True,
            "needs_review": False,
            "next_action": "Apply this plan.",
        },
        "review": {"candidate_count": 0, "candidates": []},
        "summary": {"planned_count": 1, "error_count": 0},
        "organize": {"entries": [{"source_path": "a.jpg", "target_path": "out/a.jpg", "status": "planned"}]},
    }


def test_build_report_service_bundle_combines_core_gui_artifacts() -> None:
    bundle = build_report_service_bundle(
        command_name="organize",
        report_payload=_report_payload(),
        command_payload={"argv": ["--source", "photos"], "apply_requested": False, "exit_code": 0},
        run_id="run-1",
    )

    assert bundle["kind"] == "report_service_bundle"
    assert bundle["ui_state"]["command"] == "organize"
    assert bundle["plan_snapshot"]["entry_count"] == 1
    assert bundle["action_model"]["command"] == "organize"


def test_write_report_service_bundle_writes_expected_files(tmp_path: Path) -> None:
    payload = write_report_service_bundle(
        tmp_path / "service",
        command_name="organize",
        report_payload=_report_payload(),
        command_payload={"argv": [], "apply_requested": False, "exit_code": 0},
    )

    assert (tmp_path / "service" / "ui_state.json").exists()
    assert (tmp_path / "service" / "plan_snapshot.json").exists()
    assert (tmp_path / "service" / "action_model.json").exists()
    assert (tmp_path / "service" / "service_bundle.json").exists()
    assert len(payload["written_files"]) == 4


def test_app_home_state_summarizes_profiles_runs_and_people_bundle(tmp_path: Path) -> None:
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    (profile_dir / "people.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_id": "people-review",
                "title": "People Review",
                "description": "",
                "command": "people",
                "tags": [],
                "favorite": True,
                "values": {"people_mode": "scan", "source_dirs": ["photos"]},
                "gui": {},
            }
        ),
        encoding="utf-8",
    )

    run_dir = tmp_path / "runs"
    run = run_dir / "20260101T000000Z-organize-preview"
    run.mkdir(parents=True)
    (run / "command.json").write_text(json.dumps({"command": "organize", "apply_requested": False, "exit_code": 0}), encoding="utf-8")
    (run / "report.json").write_text(json.dumps(_report_payload()), encoding="utf-8")

    bundle_dir = tmp_path / "people-bundle"
    bundle_dir.mkdir()
    (bundle_dir / "bundle_manifest.json").write_text(json.dumps({"status": "ready", "summary": {"group_count": 1}, "artifacts": {}}), encoding="utf-8")
    (bundle_dir / "people_review_workspace.json").write_text("{}", encoding="utf-8")

    state = build_app_home_state(profile_dir=profile_dir, run_dir=run_dir, people_bundle_dir=bundle_dir, active_page_id="people-review")

    assert state["profiles"]["summary"]["profile_count"] == 1
    assert state["runs"]["summary"]["run_count"] == 1
    assert state["people_review"]["ready_for_gui"] is True
    assert state["suggested_next_step"] == "Open the people review page."
    assert discover_run_summaries(run_dir)[0]["command"] == "organize"
    assert load_people_review_bundle_summary(bundle_dir)["status"] == "ready"
