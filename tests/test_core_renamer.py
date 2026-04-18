
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.renamer import (
    RenamePlannerOptions,
    build_rename_dry_run,
    execute_rename_dry_run,
    render_rename_filename,
    sanitize_filename,
)


def _resolution(path: Path, dt: datetime | None = None) -> DateResolution:
    resolved = dt or datetime(2024, 8, 10, 11, 12, 13)
    return DateResolution(
        path=path,
        resolved_datetime=resolved,
        resolved_value=resolved.strftime("%Y-%m-%d %H:%M:%S"),
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_render_rename_filename_supports_date_format_tokens() -> None:
    file_path = Path("/photos/IMG_0001.JPG")
    rendered = render_rename_filename(
        file_path,
        _resolution(file_path),
        "{date:%Y-%m-%d}_{stem}",
        index=1,
        source_root=Path("/photos"),
    )

    assert rendered == "2024-08-10_IMG_0001.JPG"


def test_render_rename_filename_supports_suffix_and_source_tokens() -> None:
    file_path = Path("/camera/DCIM/IMG_0001.JPG")
    rendered = render_rename_filename(
        file_path,
        _resolution(file_path),
        "{source_name}_{index}_{stem}{suffix}",
        index=7,
        source_root=Path("/camera/DCIM"),
    )

    assert rendered == "DCIM_0007_IMG_0001.JPG"


def test_sanitize_filename_replaces_windows_invalid_characters() -> None:
    assert sanitize_filename('bad:name*with?chars') == "bad_name_with_chars"


def test_build_rename_dry_run_marks_matching_name_as_skipped(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{stem}",
        )
    )

    assert dry_run.media_file_count == 1
    assert dry_run.skipped_count == 1
    assert dry_run.entries[0].status == "skipped"


def test_build_rename_dry_run_marks_existing_target_as_conflict(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    conflict_path = source / "2024-08-10_source.JPG"
    file_path.write_bytes(b"jpg")
    conflict_path.write_bytes(b"existing")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{date:%Y-%m-%d}_{source_name}",
        )
    )

    assert dry_run.conflict_count == 1
    assert any(item.source_path == file_path and item.status == "conflict" for item in dry_run.entries)


def test_build_rename_dry_run_detects_duplicate_target_names(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "first.JPG"
    second = source / "second.JPG"
    first.write_bytes(b"1")
    second.write_bytes(b"2")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{date:%Y-%m-%d}",
        )
    )

    assert dry_run.conflict_count == 2
    assert all(item.status == "conflict" for item in dry_run.entries)


def test_execute_rename_dry_run_preview_marks_planned_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{date:%Y-%m-%d}_{stem}",
        )
    )
    execution = execute_rename_dry_run(dry_run, apply=False)

    assert execution.preview_count == 1
    assert execution.renamed_count == 0
    assert execution.entries[0].action == "preview-rename"
    assert file_path.exists()


def test_execute_rename_dry_run_apply_renames_file(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{date:%Y-%m-%d}_{stem}",
        )
    )
    execution = execute_rename_dry_run(dry_run, apply=True)

    renamed_path = source / "2024-08-10_IMG_0001.JPG"
    assert execution.renamed_count == 1
    assert execution.entries[0].status == "renamed"
    assert not file_path.exists()
    assert renamed_path.exists()


def test_second_rename_run_becomes_skipped_due_to_matching_name(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    first_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{date:%Y-%m-%d}_{stem}",
        )
    )
    execute_rename_dry_run(first_run, apply=True)

    second_run = build_rename_dry_run(
        RenamePlannerOptions(
            source_dirs=(source,),
            template="{stem}",
        )
    )

    assert second_run.skipped_count == 1
    assert second_run.entries[0].status == "skipped"
