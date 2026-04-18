from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
    render_organize_directory,
)


def _resolution(path: Path, dt: datetime) -> DateResolution:
    return DateResolution(
        path=path,
        resolved_datetime=dt,
        resolved_value=dt.strftime("%Y-%m-%d %H:%M:%S"),
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_render_organize_directory_uses_supported_tokens() -> None:
    resolution = _resolution(Path("photo.jpg"), datetime(2024, 8, 10, 11, 12, 13))

    rendered = render_organize_directory(
        "{year}/{year_month_day}/{source_name}",
        resolution,
        source_root=Path("/imports/phone"),
    )

    assert rendered.as_posix() == "2024/2024-08-10/phone"


def test_build_organize_dry_run_plans_target_paths(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
    )

    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern=DEFAULT_ORGANIZE_PATTERN,
        )
    )

    assert plan.media_file_count == 1
    assert plan.planned_count == 1
    assert plan.conflict_count == 0

    entry = plan.entries[0]
    assert entry.status == "planned"
    assert entry.target_relative_dir.as_posix() == "2024/2024-08-10"
    assert entry.target_path == target / "2024" / "2024-08-10" / "photo.jpg"


def test_build_organize_dry_run_marks_existing_target_as_conflict(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    existing_target = target / "2024" / "2024-08-10"
    existing_target.mkdir(parents=True)
    (existing_target / "photo.jpg").write_bytes(b"existing")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
    )

    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=(source,),
            target_root=target,
            pattern=DEFAULT_ORGANIZE_PATTERN,
        )
    )

    assert plan.planned_count == 0
    assert plan.conflict_count == 1
    assert plan.entries[0].status == "conflict"
    assert plan.entries[0].reason == "target path already exists"


def test_build_organize_dry_run_marks_same_target_path_collisions(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    target = tmp_path / "target"
    source_a.mkdir()
    source_b.mkdir()
    target.mkdir()

    first = source_a / "photo.jpg"
    second = source_b / "photo.jpg"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
    )

    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=(source_a, source_b),
            target_root=target,
            pattern=DEFAULT_ORGANIZE_PATTERN,
        )
    )

    assert plan.planned_count == 0
    assert plan.conflict_count == 2
    assert {item.reason for item in plan.entries} == {
        "multiple source files would resolve to the same target path"
    }


def test_build_organize_dry_run_skips_source_already_in_target_location(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "target"
    planned_dir = target / "2024" / "2024-08-10"
    planned_dir.mkdir(parents=True)

    photo = planned_dir / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)),
    )

    plan = build_organize_dry_run(
        OrganizePlannerOptions(
            source_dirs=(planned_dir,),
            target_root=target,
            pattern=DEFAULT_ORGANIZE_PATTERN,
            recursive=False,
        )
    )

    assert plan.skipped_count == 1
    assert plan.entries[0].status == "skipped"
    assert plan.entries[0].reason == "source already matches the planned target path"
