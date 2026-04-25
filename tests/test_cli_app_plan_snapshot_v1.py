from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app import main as app_main
from media_manager.core.plan_snapshot import build_plan_snapshot_from_report
from media_manager.core.run_artifacts import write_run_artifacts
from media_manager.core.run_index import build_run_artifacts_payload, list_run_artifacts, load_run_artifact_payload


def test_build_plan_snapshot_from_organize_report_entries() -> None:
    report = {
        "outcome_report": {"status": "review_required", "safe_to_apply": False, "needs_review": True, "next_action": "Review conflicts."},
        "review": {"candidate_count": 1},
        "organize": {
            "entries": [
                {
                    "source_path": "C:/in/a.jpg",
                    "target_path": "D:/out/a.jpg",
                    "status": "conflict",
                    "reason": "target exists",
                    "group_id": "g1",
                    "group_kind": "single",
                }
            ]
        },
    }

    snapshot = build_plan_snapshot_from_report(command_name="organize", report_payload=report, run_id="run-1")

    assert snapshot["command"] == "organize"
    assert snapshot["entry_count"] == 1
    assert snapshot["overview"]["review_candidate_count"] == 1
    assert snapshot["status_summary"] == {"conflict": 1}
    assert snapshot["entries"][0]["source_path"] == "C:/in/a.jpg"
    assert snapshot["entries"][0]["review_reasons"] == ["conflict"]


def test_build_plan_snapshot_from_duplicates_decision_rows() -> None:
    report = {
        "outcome_report": {"status": "review_required", "safe_to_apply": False, "needs_review": True},
        "review": {"candidate_count": 1},
        "decision_rows": [
            {
                "group_id": "duplicate-group-1",
                "candidate_paths": ["C:/media/a.mp4", "C:/media/b.mp4"],
                "status": "needs_review",
                "reason": "missing_keep_decision",
                "extension_summary": {".mp4": 2},
                "media_kind_summary": {"video": 2},
            }
        ],
    }

    snapshot = build_plan_snapshot_from_report(command_name="duplicates", report_payload=report)

    assert snapshot["entry_count"] == 1
    assert snapshot["entries"][0]["kind"] == "duplicate_group"
    assert snapshot["entries"][0]["candidate_count"] == 2
    assert snapshot["entries"][0]["extension_summary"] == {".mp4": 2}


def test_run_artifacts_write_plan_snapshot(tmp_path: Path) -> None:
    payload = {
        "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False, "next_action": "Apply when ready."},
        "review": {"candidate_count": 0},
        "organize": {"entries": [{"source_path": "a.jpg", "target_path": "out/a.jpg", "status": "planned", "reason": "ready"}]},
    }

    paths = write_run_artifacts(
        tmp_path,
        command_name="organize",
        argv=["organize", "--run-dir", "runs"],
        apply_requested=False,
        exit_code=0,
        payload=payload,
        created_at_utc="2026-04-25T12:00:00Z",
    )

    plan_snapshot_path = Path(paths["plan_snapshot_path"])
    assert plan_snapshot_path.is_file()
    snapshot = json.loads(plan_snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["entry_count"] == 1
    assert snapshot["entries"][0]["status"] == "planned"

    records = list_run_artifacts(tmp_path)
    assert records[0].has_plan_snapshot is True
    assert build_run_artifacts_payload(records, root_dir=tmp_path)["runs"][0]["has_plan_snapshot"] is True
    assert load_run_artifact_payload(records[0].run_dir, "plan_snapshot.json")["command"] == "organize"


def test_cli_app_plan_snapshot_json(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "report.json"
    out_path = tmp_path / "plan_snapshot.json"
    report_path.write_text(
        json.dumps(
            {
                "outcome_report": {"status": "ready", "safe_to_apply": True},
                "review": {"candidate_count": 0},
                "rename": {"entries": [{"source_path": "a.jpg", "target_path": "b.jpg", "status": "planned", "reason": "ready"}]},
            }
        ),
        encoding="utf-8",
    )

    exit_code = app_main([
        "plan-snapshot",
        "--command",
        "rename",
        "--report-json",
        str(report_path),
        "--run-id",
        "run-1",
        "--out",
        str(out_path),
    ])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["command"] == "rename"
    assert payload["entries"][0]["target_path"] == "b.jpg"
    assert out_path.is_file()
