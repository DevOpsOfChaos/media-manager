from __future__ import annotations

from pathlib import Path

from media_manager.duplicate_session_store import (
    build_duplicate_group_signature,
    normalize_duplicate_decisions,
    restore_duplicate_session,
    save_duplicate_session_snapshot,
)
from media_manager.duplicates import ExactDuplicateGroup


def _group(tmp_path: Path, digest: str = 'digest') -> ExactDuplicateGroup:
    keep = tmp_path / f'keep-{digest}.jpg'
    remove = tmp_path / f'remove-{digest}.jpg'
    keep.write_bytes(b'a')
    remove.write_bytes(b'a')
    return ExactDuplicateGroup(
        files=[keep, remove],
        file_size=1,
        sample_digest='sample',
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_normalize_duplicate_decisions_discards_unknown_group_and_invalid_path(tmp_path: Path) -> None:
    group = _group(tmp_path)
    decisions = {
        'unknown': str(group.files[0]),
        '1:digest': str(tmp_path / 'other.jpg'),
        '1:digest-valid': str(group.files[0]),
    }
    # Align ids to actual group id for test clarity
    actual = {f'{group.file_size}:{group.full_digest}': str(group.files[0])}
    normalized = normalize_duplicate_decisions([group], {**decisions, **actual})

    assert normalized == actual


def test_restore_duplicate_session_reports_mismatch_for_changed_group_signature(tmp_path: Path) -> None:
    group = _group(tmp_path, digest='one')
    session_path = tmp_path / 'session.json'
    save_duplicate_session_snapshot(session_path, [group], {f'{group.file_size}:{group.full_digest}': str(group.files[0])})

    changed_group = _group(tmp_path, digest='two')
    result = restore_duplicate_session(session_path, [changed_group])

    assert result.status == 'mismatch'
    assert 'does not match' in result.reason
    assert result.snapshot is not None


def test_build_duplicate_group_signature_is_stable_for_same_group_order(tmp_path: Path) -> None:
    group = _group(tmp_path)
    first = build_duplicate_group_signature([group])
    second = build_duplicate_group_signature([group])
    assert first == second
