from pathlib import Path

from media_manager.sorter import SortConfig, build_target_dir, ensure_unique_path, organize_media


class DummyDate:
    year = 2024
    month = 7
    day = 18


def test_build_target_dir_uses_template() -> None:
    target = build_target_dir(Path("/dest"), DummyDate(), "{year}/{month}/{day}")
    assert target.as_posix() == "/dest/2024/07/18"


def test_ensure_unique_path_returns_incremented_name(tmp_path: Path) -> None:
    existing = tmp_path / "photo.jpg"
    existing.write_bytes(b"x")
    unique = ensure_unique_path(existing)
    assert unique.name == "photo_1.jpg"


def test_organize_media_processes_multiple_source_directories(tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    target = tmp_path / "target"
    source_a.mkdir()
    source_b.mkdir()
    target.mkdir()

    (source_a / "first.jpg").write_bytes(b"a")
    (source_b / "second.jpg").write_bytes(b"b")

    config = SortConfig(source_dirs=[source_a, source_b], target_dir=target, dry_run=True, mode="copy")
    result = organize_media(config)

    assert result.processed == 2
    assert result.organized == 2
    assert result.errors == 0
    assert {entry.source.name for entry in result.entries} == {"first.jpg", "second.jpg"}


def test_organize_media_deduplicates_repeated_source_directory_input(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    (source / "photo.jpg").write_bytes(b"x")

    config = SortConfig(source_dirs=[source, source], target_dir=target, dry_run=True, mode="copy")
    result = organize_media(config)

    assert result.processed == 1
    assert result.organized == 1
    assert result.errors == 0
    assert result.entries[0].source.name == "photo.jpg"


def test_organize_media_reports_progress_messages(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"x")

    messages: list[str] = []
    config = SortConfig(source_dirs=[source], target_dir=target, dry_run=True, mode="copy")
    result = organize_media(config, progress_callback=messages.append)

    assert result.processed == 1
    assert messages[0] == "Scanning source folders ..."
    assert messages[1] == "Found 1 media file."
    assert messages[2] == "Processing 1/1: photo.jpg"
    assert messages[-1] == "Finished. 1 action(s), 0 error(s)."
