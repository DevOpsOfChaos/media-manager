from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import _build_decisions, _write_json_report
from media_manager.duplicates import ExactDuplicateGroup


def _group(tmp_path: Path, name_a: str = 'keep.jpg', name_b: str = 'remove.jpg') -> ExactDuplicateGroup:
    a = tmp_path / name_a
    b = tmp_path / name_b
    a.write_bytes(b'a')
    b.write_bytes(b'b')
    return ExactDuplicateGroup(
        files=[a, b],
        file_size=1,
        sample_digest='sample',
        full_digest='digest',
        same_name=False,
        same_suffix=True,
    )


def test_build_decisions_returns_session_restore_and_keeps_existing_decisions(monkeypatch, tmp_path: Path) -> None:
    group = _group(tmp_path)
    restored = {'g1': 'keep-from-session'}
    auto = {'g1': 'keep-from-policy', 'g2': 'auto-only'}

    monkeypatch.setattr(
        'media_manager.cli_duplicates.restore_duplicate_session',
        lambda file_path, exact_groups: SimpleNamespace(
            status='matched',
            reason='ok',
            decisions=restored,
            snapshot=None,
        ),
    )
    monkeypatch.setattr('media_manager.cli_duplicates.build_duplicate_decisions', lambda exact_groups, policy: auto)

    args = SimpleNamespace(load_session=tmp_path / 'session.json', policy='first')
    decisions, session_restore = _build_decisions(SimpleNamespace(exact_groups=[group]), args)

    assert decisions == {'g1': 'keep-from-session', 'g2': 'auto-only'}
    assert session_restore.status == 'matched'
    assert session_restore.reason == 'ok'


def test_write_json_report_includes_stage_errors_and_session_restore(tmp_path: Path) -> None:
    output = tmp_path / 'report.json'

    scan_result = SimpleNamespace(
        scanned_files=3,
        size_candidate_files=2,
        hashed_files=2,
        exact_groups=[],
        exact_duplicate_files=2,
        exact_duplicates=1,
        errors=4,
        size_group_errors=1,
        sample_errors=1,
        hash_errors=1,
        compare_errors=1,
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
        executed_rows=1,
        previewed_rows=0,
        deleted_rows=1,
        deferred_rows=0,
        blocked_rows=0,
        blocked_associated_rows=0,
        blocked_missing_survivor_rows=0,
        error_rows=0,
        entries=[],
    )
    session_restore = SimpleNamespace(
        status='mismatch',
        reason='saved duplicate session does not match the current exact duplicate groups',
        decisions={},
        snapshot=SimpleNamespace(exact_group_count=2, decision_count=1),
    )

    _write_json_report(output, scan_result, bundle, execution_result, session_restore=session_restore)

    payload = json.loads(output.read_text(encoding='utf-8'))
    assert payload['scan']['stage_errors'] == {
        'size_group_errors': 1,
        'sample_errors': 1,
        'hash_errors': 1,
        'compare_errors': 1,
    }
    assert payload['session_restore']['status'] == 'mismatch'
    assert payload['session_restore']['snapshot_exact_group_count'] == 2
    assert payload['session_restore']['snapshot_decision_count'] == 1
