from __future__ import annotations

import json
import sys
import types
from pathlib import Path

from media_manager.similar_images import SimilarImageGroup, SimilarImageMember
from media_manager.similar_review import build_similar_review_report


def _install_duplicate_cli_stubs() -> None:
    session_store = types.ModuleType('media_manager.duplicate_session_store')
    session_store.restore_duplicate_decisions = lambda *args, **kwargs: {}
    session_store.save_duplicate_session_snapshot = lambda *args, **kwargs: None
    sys.modules['media_manager.duplicate_session_store'] = session_store

    workflow = types.ModuleType('media_manager.duplicate_workflow')
    workflow.build_duplicate_decisions = lambda *args, **kwargs: {}
    workflow.build_duplicate_workflow_bundle = lambda *args, **kwargs: None
    workflow.execute_duplicate_workflow_bundle = lambda *args, **kwargs: None
    sys.modules['media_manager.duplicate_workflow'] = workflow


def test_write_json_report_includes_review_priority_fields(monkeypatch, tmp_path: Path) -> None:
    _install_duplicate_cli_stubs()
    from media_manager.cli_duplicates import _write_json_report

    class ExactResult:
        scanned_files = 1
        size_candidate_files = 0
        hashed_files = 0
        exact_groups = []
        exact_duplicate_files = 0
        exact_duplicates = 0
        errors = 0

    class CleanupPlan:
        total_groups = 0
        resolved_groups = 0
        unresolved_groups = 0
        planned_removals = []
        estimated_reclaimable_bytes = 0

    class DryRun:
        ready = True
        planned_count = 0
        blocked_count = 0
        delete_count = 0
        exclude_from_copy_count = 0
        exclude_from_move_count = 0
        planned_actions = []
        blocked_actions = []

    class ExecutionPreview:
        ready = True
        executable_count = 0
        deferred_count = 0
        blocked_count = 0
        delete_count = 0
        rows = []

    class Bundle:
        decisions = {}
        cleanup_plan = CleanupPlan()
        dry_run = DryRun()
        execution_preview = ExecutionPreview()

    class SimilarResult:
        scanned_files = 1
        image_files = 3
        hashed_files = 3
        similar_pairs = 2
        errors = 0
        similar_groups = [
            SimilarImageGroup(
                anchor_path=Path('/photos/keep.jpg'),
                members=[
                    SimilarImageMember(path=Path('/photos/keep.jpg'), hash_hex='0f', distance=0),
                    SimilarImageMember(path=Path('/photos/exact.jpg'), hash_hex='0f', distance=0),
                    SimilarImageMember(path=Path('/photos/close.jpg'), hash_hex='0e', distance=1),
                ],
            )
        ]

    report = build_similar_review_report(SimilarResult.similar_groups, keep_policy='first')
    report_path = tmp_path / 'report.json'
    _write_json_report(report_path, ExactResult(), Bundle(), None, similar_result=SimilarResult(), similar_review=report)

    payload = json.loads(report_path.read_text(encoding='utf-8'))
    assert payload['similar_review']['high_priority_count'] == 2
    assert payload['similar_review']['exact_hash_review_count'] == 1
    row = payload['similar_review']['rows'][1]
    assert row['match_kind'] == 'exact-hash'
    assert row['review_priority'] == 'high'
