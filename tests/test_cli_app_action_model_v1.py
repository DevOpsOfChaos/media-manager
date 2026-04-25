from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app import main as app_main
from media_manager.cli_runs import main as runs_main
from media_manager.core.action_model import build_action_model_from_report
from media_manager.core.run_artifacts import write_run_artifacts
from media_manager.core.run_index import build_run_artifacts_payload, list_run_artifacts, load_run_artifact_payload


def test_build_action_model_enables_clean_organize_apply() -> None:
    payload = {
        "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False, "next_action": "Apply when ready."},
        "review": {"candidate_count": 0},
        "organize": {"planned_count": 1, "conflict_count": 0, "error_count": 0},
    }

    model = build_action_model_from_report(
        command_name="organize",
        report_payload=payload,
        command_payload={"argv": ["--source", "in", "--target", "out"], "apply_requested": False},
        run_id="run-1",
    )

    apply_action = next(item for item in model["actions"] if item["id"] == "apply_plan")
    assert model["next_action_id"] == "apply_plan"
    assert apply_action["enabled"] is True
    assert apply_action["requires_confirmation"] is True
    assert "--apply" in apply_action["command_preview"]


def test_build_action_model_blocks_duplicate_apply_without_reviewed_decisions() -> None:
    payload = {
        "outcome_report": {"status": "review_required", "safe_to_apply": False, "needs_review": True},
        "review": {"candidate_count": 2},
        "decision_summary": {"resolved_group_count": 0, "unresolved_group_count": 2, "from_decision_file_count": 0},
    }

    model = build_action_model_from_report(command_name="duplicates", report_payload=payload)

    apply_action = next(item for item in model["actions"] if item["id"] == "apply_duplicate_cleanup")
    export_action = next(item for item in model["actions"] if item["id"] == "export_duplicate_decisions")
    assert apply_action["enabled"] is False
    assert apply_action["risk_level"] == "destructive"
    assert export_action["recommended"] is True


def test_run_artifacts_write_action_model(tmp_path: Path) -> None:
    payload = {
        "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False, "next_action": "Apply when ready."},
        "review": {"candidate_count": 0, "reason_summary": {}},
        "rename": {"planned_count": 1, "conflict_count": 0, "error_count": 0},
    }

    paths = write_run_artifacts(
        tmp_path,
        command_name="rename",
        argv=["rename", "--source", "in"],
        apply_requested=False,
        exit_code=0,
        payload=payload,
        created_at_utc="2026-04-25T12:00:00Z",
    )

    action_model_path = Path(paths["action_model_path"])
    assert action_model_path.is_file()
    model = json.loads(action_model_path.read_text(encoding="utf-8"))
    assert model["command"] == "rename"
    assert model["action_count"] >= 1

    records = list_run_artifacts(tmp_path)
    assert records[0].has_action_model is True
    row = build_run_artifacts_payload(records, root_dir=tmp_path)["runs"][0]
    assert row["has_action_model"] is True
    assert row["action_count"] == model["action_count"]
    assert load_run_artifact_payload(records[0].run_dir, "action_model.json")["command"] == "rename"


def test_cli_app_action_model_json(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "report.json"
    command_path = tmp_path / "command.json"
    out_path = tmp_path / "action_model.json"
    report_path.write_text(
        json.dumps(
            {
                "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False},
                "review": {"candidate_count": 0},
                "organize": {"planned_count": 1},
            }
        ),
        encoding="utf-8",
    )
    command_path.write_text(json.dumps({"argv": ["--source", "in", "--target", "out"], "apply_requested": False}), encoding="utf-8")

    exit_code = app_main([
        "action-model",
        "--command",
        "organize",
        "--report-json",
        str(report_path),
        "--command-json",
        str(command_path),
        "--run-id",
        "run-1",
        "--out",
        str(out_path),
    ])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["command"] == "organize"
    assert payload["next_action_id"] == "apply_plan"
    assert out_path.is_file()


def test_runs_show_action_model(tmp_path: Path, capsys) -> None:
    run_root = tmp_path / "runs"
    paths = write_run_artifacts(
        run_root,
        command_name="organize",
        argv=["organize", "--source", "in", "--target", "out"],
        apply_requested=False,
        exit_code=0,
        payload={
            "outcome_report": {"status": "ready", "safe_to_apply": True, "needs_review": False},
            "review": {"candidate_count": 0},
            "organize": {"planned_count": 1},
        },
        created_at_utc="2026-04-25T12:00:00Z",
    )

    exit_code = runs_main(["--run-dir", str(run_root), "show", Path(paths["run_dir"]).name, "--artifact", "action-model"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["command"] == "organize"
    assert payload["action_count"] >= 1
