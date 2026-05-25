from __future__ import annotations

from pathlib import Path

from media_manager.core.leftover import (
    LeftoverConsolidationResult,
    discover_leftover_files,
    execute_leftover_consolidation,
    remove_empty_directories,
    resolve_leftover_target,
)


def test_discover_leftover_files_finds_regular_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    (source / "notes.txt").write_bytes(b"text")

    files = discover_leftover_files(source, "_leftover")

    assert len(files) == 2
    assert source / "photo.jpg" in files
    assert source / "notes.txt" in files


def test_discover_leftover_files_excludes_leftover_dir(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    leftover = source / "_leftover"
    leftover.mkdir()
    (source / "keep.jpg").write_bytes(b"jpg")
    (leftover / "already_moved.jpg").write_bytes(b"jpg")

    files = discover_leftover_files(source, "_leftover")

    assert len(files) == 1
    assert files[0] == source / "keep.jpg"


def test_discover_leftover_files_handles_nested_dirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    sub = source / "sub"
    sub.mkdir()
    (source / "root_file.jpg").write_bytes(b"jpg")
    (sub / "nested_file.jpg").write_bytes(b"jpg")

    files = discover_leftover_files(source, "_leftover")

    assert len(files) == 2


def test_discover_leftover_files_empty_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    
    files = discover_leftover_files(source, "_leftover")
    
    assert files == []


def test_discover_leftover_files_nonexistent_source(tmp_path: Path) -> None:
    source = tmp_path / "nonexistent"
    
    files = discover_leftover_files(source, "_leftover")
    
    assert files == []


def test_resolve_leftover_target_no_collision(tmp_path: Path) -> None:
    leftover = tmp_path / "_leftover"
    leftover.mkdir()
    
    target, conflict = resolve_leftover_target(leftover, "photo.jpg")
    
    assert target == leftover / "photo.jpg"
    assert conflict is False


def test_resolve_leftover_target_with_collision(tmp_path: Path) -> None:
    leftover = tmp_path / "_leftover"
    leftover.mkdir()
    (leftover / "photo.jpg").write_bytes(b"existing")
    
    target, conflict = resolve_leftover_target(leftover, "photo.jpg")
    
    assert target == leftover / "photo__2.jpg"
    assert conflict is True


def test_remove_empty_directories_cleans_empty_subdirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    empty_sub = source / "empty_sub"
    empty_sub.mkdir()
    nested = source / "a" / "b"
    nested.mkdir(parents=True)
    
    removed = remove_empty_directories(source, "_leftover")

    assert not (source / "empty_sub").exists()
    assert not (source / "a" / "b").exists()


def test_remove_empty_directories_keeps_nonempty(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    has_file = source / "has_file"
    has_file.mkdir()
    (has_file / "keep.jpg").write_bytes(b"jpg")
    
    removed = remove_empty_directories(source, "_leftover")
    
    assert (source / "has_file").exists()


def test_remove_empty_directories_excludes_leftover(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    leftover = source / "_leftover"
    leftover.mkdir()
    
    removed = remove_empty_directories(source, "_leftover")
    
    assert leftover.exists()


def test_execute_leftover_consolidation_moves_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    jpg = source / "photo.jpg"
    txt = source / "notes.txt"
    jpg.write_bytes(b"jpg")
    txt.write_bytes(b"text")

    result = execute_leftover_consolidation((source,), "_remaining")

    assert result.file_count == 2
    assert result.error_count == 0
    assert not jpg.exists()
    assert not txt.exists()
    assert (source / "_remaining" / "photo.jpg").exists()
    assert (source / "_remaining" / "notes.txt").exists()


def test_execute_leftover_consolidation_removes_empty_dirs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    empty_sub = source / "empty"
    empty_sub.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    result = execute_leftover_consolidation((source,), "_remaining")

    assert result.file_count == 1
    assert not empty_sub.exists()
    assert result.removed_empty_directory_count >= 1


def test_execute_leftover_consolidation_handles_collision(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    leftover = source / "_remaining"
    leftover.mkdir()
    (leftover / "photo.jpg").write_bytes(b"existing")
    (source / "photo.jpg").write_bytes(b"new")

    result = execute_leftover_consolidation((source,), "_remaining")

    assert result.file_count == 1
    assert result.conflict_count == 1
    assert (leftover / "photo__2.jpg").exists()


def test_execute_leftover_consolidation_empty_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    result = execute_leftover_consolidation((source,), "_remaining")

    assert result.file_count == 0
    assert result.error_count == 0
