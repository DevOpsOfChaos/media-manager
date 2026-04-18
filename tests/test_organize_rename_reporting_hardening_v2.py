from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.organizer import OrganizePlannerOptions, build_organize_dry_run, execute_organize_plan
from media_manager.core.renamer import RenamePlannerOptions, build_rename_dry_run, execute_rename_dry_run


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


def test_organize_dry_run_exposes_reason_and_resolution_summaries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    first = source / "first.jpg"
    second = source / "second.jpg"
    first.write_bytes(b"one")
    second.write_bytes(b"two")

    existing_dir = target / "2024" / "2024-08-10"
    existing_dir.mkdir(parents=True)
    (existing_dir / "first.jpg").write_bytes(b"existing-other")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_organize_dry_run(
        OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern="{year}/{year_month_day}")
    )

    assert dry_run.status_summary == {"conflict": 1, "planned": 1}
    assert dry_run.reason_summary["target path already exists"] == 1
    assert dry_run.reason_summary["ready for organize execution"] == 1
    assert dry_run.resolution_source_summary == {"metadata": 2}
    assert dry_run.confidence_summary == {"high": 2}


def test_organize_execution_result_exposes_outcome_and_reason_summaries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_organize_dry_run(
        OrganizePlannerOptions(source_dirs=(source,), target_root=target, pattern="{year}/{year_month_day}")
    )
    execution = execute_organize_plan(dry_run)

    assert execution.outcome_summary == {"copied": 1}
    assert execution.reason_summary == {"executed organize action": 1}


def test_rename_dry_run_exposes_reason_and_resolution_summaries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "IMG_0001.JPG"
    second = source / "IMG_0002.JPG"
    first.write_bytes(b"1")
    second.write_bytes(b"2")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(RenamePlannerOptions(source_dirs=(source,), template="{date:%Y-%m-%d}"))

    assert dry_run.status_summary == {"conflict": 2}
    assert dry_run.reason_summary == {"multiple source files would resolve to the same target file name": 2}
    assert dry_run.resolution_source_summary == {"metadata": 2}
    assert dry_run.confidence_summary == {"high": 2}


def test_rename_execution_result_exposes_status_action_and_reason_summaries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "IMG_0001.JPG"
    file_path.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    dry_run = build_rename_dry_run(RenamePlannerOptions(source_dirs=(source,), template="{date:%Y-%m-%d}_{stem}"))
    execution = execute_rename_dry_run(dry_run, apply=False)

    assert execution.status_summary == {"planned": 1}
    assert execution.action_summary == {"preview-rename": 1}
    assert execution.reason_summary == {"ready for rename execution": 1}
