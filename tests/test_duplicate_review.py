import os
from pathlib import Path

from media_manager.duplicate_review import (
    count_marked_for_removal,
    default_keep_path,
    newest_keep_path,
    oldest_keep_path,
    paths_marked_for_removal,
)


def test_default_keep_path_uses_stable_sorted_path(tmp_path: Path) -> None:
    second = tmp_path / "b.jpg"
    first = tmp_path / "a.jpg"
    first.write_bytes(b"1")
    second.write_bytes(b"1")

    assert default_keep_path([second, first]) == first


def test_newest_and_oldest_keep_path_use_mtime(tmp_path: Path) -> None:
    old = tmp_path / "old.jpg"
    new = tmp_path / "new.jpg"
    old.write_bytes(b"1")
    new.write_bytes(b"1")

    os.utime(old, ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000))
    os.utime(new, ns=(1_800_000_000_000_000_000, 1_800_000_000_000_000_000))

    assert newest_keep_path([old, new]) == new
    assert oldest_keep_path([old, new]) == old


def test_paths_marked_for_removal_keep_only_selected_file(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove_a = tmp_path / "remove_a.jpg"
    remove_b = tmp_path / "remove_b.jpg"
    for path in [keep, remove_a, remove_b]:
        path.write_bytes(b"1")

    marked = paths_marked_for_removal([keep, remove_a, remove_b], keep)

    assert marked == [remove_a, remove_b]
    assert count_marked_for_removal([keep, remove_a, remove_b], keep) == 2
