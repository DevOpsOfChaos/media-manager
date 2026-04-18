from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state import build_history_artifact_paths, write_history_artifacts


def test_build_history_artifact_paths_uses_expected_names() -> None:
    result = build_history_artifact_paths(
        "history",
        command_name="organize",
        apply_requested=False,
        created_at_utc="2026-04-18T10:11:12+00:00",
    )

    assert result["created_at_utc"] == "2026-04-18T10:11:12+00:00"
    assert str(result["run_log_path"]).endswith("20260418T101112Z-organize-preview-run-log.json")


def test_write_history_artifacts_writes_shared_timestamp_for_log_and_journal(tmp_path: Path) -> None:
    result = write_history_artifacts(
        tmp_path / "history",
        command_name="rename",
        apply_requested=True,
        exit_code=0,
        payload={"planned_count": 2},
        journal_entries=[
            {
                "source_path": "a.jpg",
                "target_path": "b.jpg",
                "outcome": "renamed",
                "reason": "applied",
                "reversible": True,
            }
        ],
        created_at_utc="2026-04-18T10:11:12+00:00",
    )

    run_log_path = result["run_log_path"]
    journal_path = result["execution_journal_path"]

    assert run_log_path.name == "20260418T101112Z-rename-apply-run-log.json"
    assert journal_path.name == "20260418T101112Z-rename-apply-execution-journal.json"

    run_log = json.loads(run_log_path.read_text(encoding="utf-8"))
    journal = json.loads(journal_path.read_text(encoding="utf-8"))

    assert run_log["created_at_utc"] == "2026-04-18T10:11:12+00:00"
    assert journal["created_at_utc"] == "2026-04-18T10:11:12+00:00"
    assert run_log["payload"]["planned_count"] == 2
    assert journal["entries"][0]["outcome"] == "renamed"
