from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import (
    _build_decision_summary,
    _execution_preview_reason_summary,
    _write_json_report,
)
from media_manager.cleanup_plan import UnresolvedExactGroup
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_plan import ExecutionPreviewRow


def _group(tmp_path: Path, name_a: str = 'keep.jpg', name_b: str = 'remove.jpg', digest: str = 'digest') -> ExactDuplicateGroup:
    a = tmp_path / name_a
    b = tmp_path / name_b
    a.write_bytes(b'a')
    b.write_bytes(b'b')
    return ExactDuplicateGroup(
        files=[a, b],
        file_size=1,
        sample_digest='sample',
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_build_decision_summary_tracks_session_and_policy_sources(tmp_path: Path) -> None:
    first = _group(tmp_path, digest='one')
    second = _group(tmp_path, name_a='keep2.jpg', name_b='remove2.jpg', digest='two')
    session_restore = SimpleNamespace(status='matched', decisions={f'1:{first.full_digest}': str(first.files[0])})
    decisions = {
        f'1:{first.full_digest}': str(first.files[0]),
        f'1:{second.full_digest}': str(second.files[0]),
    }

    summary = _build_decision_summary([first, second], decisions, session_restore)

    assert summary['total_groups'] == 2
    assert summary['decided_groups'] == 2
    assert summary['undecided_groups'] == 0
    assert summary['from_session_count'] == 1
    assert summary['from_policy_count'] == 1
    assert summary['session_status'] == 'matched'


def test_execution_preview_reason_summary_groups_reasons() -> None:
    preview = SimpleNamespace(
        rows=[
            ExecutionPreviewRow('filesystem_delete', 'executable', 'g1', 'delete', Path('a'), Path('keep'), None, 1, 'exact_duplicate_remove_candidate'),
            ExecutionPreviewRow('pipeline_exclusion', 'deferred', 'g2', 'copy', Path('b'), Path('keep'), Path('target'), 1, 'exact_duplicate_remove_candidate'),
            ExecutionPreviewRow('blocked', 'blocked', 'g3', 'delete', Path('c'), None, None, 1, 'missing_keep_decision'),
            ExecutionPreviewRow('blocked_associated_files', 'blocked', 'g4', 'delete', Path('d'), Path('keep'), None, 1, 'associated_files_present'),
        ]
    )

    summary = _execution_preview_reason_summary(preview)

    assert summary['executable'] == {'exact_duplicate_remove_candidate': 1}
    assert summary['deferred'] == {'exact_duplicate_remove_candidate': 1}
    assert summary['blocked'] == {'missing_keep_decision': 1, 'associated_files_present': 1}


def test_write_json_report_includes_decision_summary_and_unresolved_payload(tmp_path: Path) -> None:
    output = tmp_path / 'report.json'
    group = _group(tmp_path)
    scan_result = SimpleNamespace(
        scanned_files=2,
        size_candidate_files=2,
        hashed_files=2,
        exact_groups=[group],
        exact_duplicate_files=2,
        exact_duplicates=1,
        errors=0,
        size_group_errors=0,
        sample_errors=0,
        hash_errors=0,
        compare_errors=0,
    )
    unresolved = [UnresolvedExactGroup(group_id='g1', candidate_paths=group.files, file_size=1)]
    bundle = SimpleNamespace(
        decisions={},
        cleanup_plan=SimpleNamespace(
            total_groups=1,
            resolved_groups=0,
            unresolved_groups=1,
            unresolved=unresolved,
            planned_removals=[],
            estimated_reclaimable_bytes=0,
        ),
        dry_run=SimpleNamespace(
            ready=False,
            planned_count=0,
            blocked_count=2,
            delete_count=0,
            exclude_from_copy_count=0,
            exclude_from_move_count=0,
            planned_actions=[],
            blocked_actions=[],
        ),
        execution_preview=SimpleNamespace(
            ready=False,
            executable_count=0,
            deferred_count=0,
            blocked_count=2,
            delete_count=0,
            rows=[ExecutionPreviewRow('blocked', 'blocked', 'g1', 'delete', group.files[0], None, None, 1, 'missing_keep_decision')],
        ),
    )

    _write_json_report(output, scan_result, bundle, None, session_restore=None)
    payload = json.loads(output.read_text(encoding='utf-8'))

    assert payload['decision_summary']['undecided_groups'] == 1
    assert payload['decision_summary']['unresolved_group_ids'] == ['1:digest']
    assert payload['cleanup_plan']['unresolved'][0]['candidate_count'] == 2
    assert payload['execution_preview']['reason_summary']['blocked'] == {'missing_keep_decision': 1}
