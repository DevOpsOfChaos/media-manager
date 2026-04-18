from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import _write_json_report


def test_write_json_report_includes_new_execution_counters(tmp_path: Path) -> None:
    output = tmp_path / "report.json"

    scan_result = SimpleNamespace(
        scanned_files=2,
        size_candidate_files=2,
        hashed_files=2,
        exact_groups=[],
        exact_duplicate_files=2,
        exact_duplicates=1,
        errors=0,
    )
    bundle = SimpleNamespace(
        decisions={},
        cleanup_plan=SimpleNamespace(
            total_groups=1,
            resolved_groups=1,
            unresolved_groups=0,
            planned_removals=[1],
            estimated_reclaimable_bytes=123,
        ),
        dry_run=SimpleNamespace(
            ready=True,
            planned_count=1,
            blocked_count=0,
            delete_count=1,
            exclude_from_copy_count=0,
            exclude_from_move_count=0,
            planned_actions=[],
            blocked_actions=[],
        ),
        execution_preview=SimpleNamespace(
            ready=True,
            executable_count=1,
            deferred_count=0,
            blocked_count=0,
            delete_count=1,
            rows=[],
        ),
    )
    execution_result = SimpleNamespace(
        processed_rows=1,
        executable_rows=1,
        executed_rows=0,
        previewed_rows=0,
        deleted_rows=0,
        deferred_rows=0,
        blocked_rows=1,
        blocked_associated_rows=0,
        blocked_missing_survivor_rows=1,
        error_rows=0,
        entries=[],
    )

    _write_json_report(output, scan_result, bundle, execution_result)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["execution_run"]["previewed_rows"] == 0
    assert payload["execution_run"]["deleted_rows"] == 0
    assert payload["execution_run"]["blocked_associated_rows"] == 0
    assert payload["execution_run"]["blocked_missing_survivor_rows"] == 1
