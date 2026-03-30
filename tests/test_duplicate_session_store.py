from __future__ import annotations

from pathlib import Path

from media_manager.duplicates import ExactDuplicateGroup
from media_manager.duplicate_session_store import (
    build_duplicate_group_signature,
    load_duplicate_session_snapshot,
    normalize_duplicate_decisions,
    restore_duplicate_decisions,
    save_duplicate_session_snapshot,
)



def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )



def test_build_duplicate_group_signature_is_stable_for_same_groups(tmp_path: Path) -> None:
    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    groups = [_group([first, second], digest="stable")]

    signature_a = build_duplicate_group_signature(groups)
    signature_b = build_duplicate_group_signature(groups)

    assert signature_a == signature_b
    assert signature_a != "empty"



def test_normalize_duplicate_decisions_drops_unknown_groups_and_invalid_paths(tmp_path: Path) -> None:
    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    third = tmp_path / "c.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")
    third.write_bytes(b"c")

    group = _group([first, second], digest="normalize")
    valid_group_id = build_duplicate_group_signature([group]).split(":", 1)[0]
    normalized = normalize_duplicate_decisions(
        [group],
        {
            valid_group_id: str(first),
            "unknown-group": str(third),
            valid_group_id + "-invalid": str(first),
        },
    )

    assert normalized == {valid_group_id: str(first)}



def test_save_and_load_duplicate_session_snapshot_roundtrip(tmp_path: Path) -> None:
    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    group = _group([first, second], digest="roundtrip")
    snapshot_path = tmp_path / "snapshot.json"

    snapshot = save_duplicate_session_snapshot(snapshot_path, [group], {build_duplicate_group_signature([group]).split(":", 1)[0]: str(first)})
    loaded = load_duplicate_session_snapshot(snapshot_path)

    assert snapshot.group_signature == loaded.group_signature
    assert snapshot.decisions == loaded.decisions



def test_restore_duplicate_decisions_returns_empty_for_signature_mismatch(tmp_path: Path) -> None:
    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    third = tmp_path / "c.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")
    third.write_bytes(b"c")

    original_group = _group([first, second], digest="orig")
    changed_group = _group([first, third], digest="changed")
    snapshot_path = tmp_path / "snapshot.json"

    original_group_id = build_duplicate_group_signature([original_group]).split(":", 1)[0]
    save_duplicate_session_snapshot(snapshot_path, [original_group], {original_group_id: str(first)})

    restored = restore_duplicate_decisions(snapshot_path, [changed_group])

    assert restored == {}



def test_restore_duplicate_decisions_returns_normalized_decisions_for_matching_signature(tmp_path: Path) -> None:
    first = tmp_path / "a.jpg"
    second = tmp_path / "b.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    group = _group([first, second], digest="match")
    snapshot_path = tmp_path / "snapshot.json"
    group_id = build_duplicate_group_signature([group]).split(":", 1)[0]

    save_duplicate_session_snapshot(snapshot_path, [group], {group_id: str(first)})
    restored = restore_duplicate_decisions(snapshot_path, [group])

    assert restored == {group_id: str(first)}
