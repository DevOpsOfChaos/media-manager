from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_runs import main as runs_main
from media_manager.core.run_artifacts import write_run_artifacts


def test_runs_list_and_show_summary(capsys, tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    payload = {
        "outcome_report": {
            "status": "ready",
            "safe_to_apply": True,
            "needs_review": False,
            "next_action": "Apply when ready.",
        },
        "review": {"candidate_count": 0, "reason_summary": {}},
        "summary": {"planned_count": 1, "error_count": 0},
    }
    paths = write_run_artifacts(
        run_root,
        command_name="organize",
        argv=["organize", "--source", "in"],
        apply_requested=False,
        exit_code=0,
        payload=payload,
        review_payload={"command": "organize", "review": {"candidate_count": 0}},
        created_at_utc="2026-04-25T10:00:00Z",
    )

    exit_code = runs_main(["--run-dir", str(run_root), "list", "--limit", "10"])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Run artifacts" in out
    assert "organize" in out
    assert Path(paths["run_dir"]).name in out

    exit_code = runs_main(["--run-dir", str(run_root), "show", Path(paths["run_dir"]).name])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Command: organize" in out
    assert "Status: ready" in out


def test_runs_json_and_validate_detect_missing_files(capsys, tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    paths = write_run_artifacts(
        run_root,
        command_name="duplicates",
        argv=["duplicates"],
        apply_requested=False,
        exit_code=0,
        payload={"outcome_report": {"status": "review_required"}, "review": {"candidate_count": 2}},
        review_payload={"command": "duplicates", "review": {"candidate_count": 2}},
        created_at_utc="2026-04-25T11:00:00Z",
    )
    Path(paths["run_dir"], "review.json").unlink()

    exit_code = runs_main(["--run-dir", str(run_root), "--json", "list"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["run_count"] == 1
    assert payload["invalid_count"] == 1
    assert payload["runs"][0]["missing_files"] == ["review.json"]

    exit_code = runs_main(["--run-dir", str(run_root), "validate"])
    assert exit_code == 1
