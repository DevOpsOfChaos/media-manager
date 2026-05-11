from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.organizer import (
    DEFAULT_ORGANIZE_PATTERN,
    OrganizePlannerOptions,
    build_organize_dry_run,
    execute_organize_plan,
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
    rendered = render_organize_directory("{year}/{year_month_day}/{source_name}", resolution, source_root=Path("/imports/phone"))
    assert rendered.as_posix() == "2024/2024-08-10/phone"


def test_build_organize_dry_run_plans_target_paths(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.media_file_count == 1
    assert plan.planned_count == 1
    assert plan.conflict_count == 0
    entry = plan.entries[0]
    assert entry.status == "planned"
    assert entry.target_relative_dir.as_posix() == "2024/2024-08-10"
    assert entry.target_path == target / "2024" / "2024-08-10" / "photo.jpg"


def test_build_organize_dry_run_marks_existing_target_as_conflict_when_bytes_differ(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-size-a")
    existing_target = target / "2024" / "2024-08-10"
    existing_target.mkdir(parents=True)
    (existing_target / "photo.jpg").write_bytes(b"same-size-b")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.planned_count == 0
    assert plan.conflict_count == 1
    assert plan.entries[0].status == "conflict"
    assert plan.entries[0].reason == "target path already exists"


def test_build_organize_dry_run_skips_existing_identical_target(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-bytes")
    existing_target = target / "2024" / "2024-08-10"
    existing_target.mkdir(parents=True)
    (existing_target / "photo.jpg").write_bytes(b"same-bytes")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.skipped_count == 1
    assert plan.entries[0].status == "skipped"
    assert plan.entries[0].reason == "target already exists with identical file content"


def test_build_organize_dry_run_marks_same_target_path_collisions(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"; source_b = tmp_path / "source_b"; target = tmp_path / "target"
    source_a.mkdir(); source_b.mkdir(); target.mkdir()
    (source_a / "photo.jpg").write_bytes(b"a")
    (source_b / "photo.jpg").write_bytes(b"b")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source_a, source_b), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN))
    assert plan.planned_count == 0
    assert plan.conflict_count == 2
    assert {item.reason for item in plan.entries} == {"multiple source files would resolve to the same target path"}


def test_build_organize_dry_run_skips_source_already_in_target_location(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "target"
    planned_dir = target / "2024" / "2024-08-10"
    planned_dir.mkdir(parents=True)
    photo = planned_dir / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(planned_dir,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, recursive=False))
    assert plan.skipped_count == 1
    assert plan.entries[0].status == "skipped"
    assert plan.entries[0].reason == "source already matches the planned target path"


def test_execute_organize_plan_copies_planned_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="copy"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.copied_count == 1
    assert result.error_count == 0
    assert photo.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_execute_organize_plan_moves_planned_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="move"))
    result = execute_organize_plan(plan)
    assert result.executed_count == 1
    assert result.moved_count == 1
    assert result.error_count == 0
    assert not photo.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_execute_organize_plan_skips_identical_target_that_appears_after_planning(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"; target = tmp_path / "target"
    source.mkdir(); target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"same-bytes")
    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path, datetime(2024, 8, 10, 11, 12, 13)))
    plan = build_organize_dry_run(OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern=DEFAULT_ORGANIZE_PATTERN, operation_mode="copy"))
    plan.entries[0].target_path.parent.mkdir(parents=True)
    plan.entries[0].target_path.write_bytes(b"same-bytes")
    result = execute_organize_plan(plan)
    assert result.executed_count == 0
    assert result.skipped_count == 1
    assert result.entries[0].reason == "target already exists with identical file content at apply time"
