
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.workflows import CleanupWorkflowOptions, build_cleanup_dry_run


def _resolution(path: Path) -> DateResolution:
    return DateResolution(
        path=path,
        resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
        resolved_value="2024-08-10 11:12:13",
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_build_cleanup_dry_run_aggregates_duplicates_organize_and_rename(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "a"
    source_b = tmp_path / "b"
    source_a.mkdir()
    source_b.mkdir()

    (source_a / "one.jpg").write_bytes(b"duplicate-bytes")
    (source_b / "two.jpg").write_bytes(b"duplicate-bytes")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    dry_run = build_cleanup_dry_run(
        CleanupWorkflowOptions(
            source_dirs=(source_a, source_b),
            target_root=tmp_path / "target",
            duplicate_policy="first",
        )
    )

    assert dry_run.media_file_count == 2
    assert dry_run.duplicate_group_count == 1
    assert dry_run.duplicate_decision_count == 1
    assert dry_run.organize_plan.planned_count == 2
    assert dry_run.rename_plan.planned_count == 2
    assert dry_run.duplicate_bundle.cleanup_plan.resolved_groups == 1
