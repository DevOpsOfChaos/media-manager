from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import main


def test_cli_duplicates_writes_run_log_and_execution_journal(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    monkeypatch.setattr("media_manager.cli_duplicates.scan_exact_duplicates", lambda config: SimpleNamespace(
        scanned_files=1,
        size_candidate_files=0,
        hashed_files=0,
        exact_groups=[],
        exact_duplicate_files=0,
        exact_duplicates=0,
        errors=0,
        size_group_errors=0,
        sample_errors=0,
        hash_errors=0,
        compare_errors=0,
    ))
    monkeypatch.setattr("media_manager.cli_duplicates.build_duplicate_workflow_bundle", lambda *args, **kwargs: SimpleNamespace(
        decisions={},
        cleanup_plan=SimpleNamespace(total_groups=0, resolved_groups=0, unresolved_groups=0, planned_removals=[], estimated_reclaimable_bytes=0, unresolved=[]),
        dry_run=SimpleNamespace(ready=True, planned_count=0, blocked_count=0, delete_count=0, exclude_from_copy_count=0, exclude_from_move_count=0, planned_actions=[], blocked_actions=[]),
        execution_preview=SimpleNamespace(ready=True, executable_count=1, deferred_count=0, blocked_count=0, delete_count=1, rows=[]),
    ))
    monkeypatch.setattr("media_manager.cli_duplicates.execute_duplicate_workflow_bundle", lambda bundle, apply=False: SimpleNamespace(
        processed_rows=1,
        executable_rows=1,
        executed_rows=1,
        deferred_rows=0,
        blocked_rows=0,
        error_rows=0,
        previewed_rows=0,
        deleted_rows=1,
        entries=[SimpleNamespace(row_type="filesystem_delete", status="executable", source_path=source / "a.jpg", survivor_path=None, target_path=None, outcome="deleted", reason="exact_duplicate_remove_candidate")],
    ))

    captured_run_log: dict[str, object] = {}
    captured_journal: dict[str, object] = {}

    def _capture_run_log(path, **kwargs):
        captured_run_log.update(kwargs)
        return path

    def _capture_journal(path, **kwargs):
        captured_journal.update(kwargs)
        return path

    monkeypatch.setattr("media_manager.cli_duplicates.write_command_run_log", _capture_run_log)
    monkeypatch.setattr("media_manager.cli_duplicates.write_execution_journal", _capture_journal)

    exit_code = main([
        "--source", str(source),
        "--mode", "delete",
        "--apply",
        "--yes",
        "--run-log", str(tmp_path / "run.json"),
        "--journal", str(tmp_path / "journal.json"),
    ])

    assert exit_code == 0
    assert captured_run_log["command_name"] == "duplicates"
    assert captured_run_log["payload"]["execution_run"]["outcome_summary"]["deleted"] == 1
    assert captured_journal["command_name"] == "duplicates"
    assert captured_journal["entries"][0]["outcome"] == "deleted"
