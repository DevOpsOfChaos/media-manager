from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import DateResolution
from media_manager.core.workflows import (
    CleanupWorkflowOptions,
    build_cleanup_workflow_report,
    execute_cleanup_workflow,
)


def _resolution(path: Path) -> DateResolution:
    resolved = datetime(2024, 8, 10, 11, 12, 13)
    return DateResolution(
        path=path,
        resolved_datetime=resolved,
        resolved_value="2024-08-10 11:12:13",
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_build_cleanup_workflow_report_combines_sections(monkeypatch, tmp_path: Path) -> None:
    source_a = tmp_path / "source_a"
    source_b = tmp_path / "source_b"
    target = tmp_path / "target"
    source_a.mkdir()
    source_b.mkdir()
    target.mkdir()

    (source_a / "IMG_20240810_111213.JPG").write_bytes(b"duplicate-bytes")
    (source_b / "IMG_20240810_111213.JPG").write_bytes(b"duplicate-bytes")
    (source_b / "UNIQUE_20240810_111214.JPG").write_bytes(b"unique")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    report = build_cleanup_workflow_report(
        CleanupWorkflowOptions(
            source_dirs=(source_a, source_b),
            target_root=target,
            organize_pattern="{year_month_day}/{source_name}",
            rename_template="{date:%Y-%m-%d_%H-%M-%S}_{source_name}_{stem}",
            duplicate_policy="first",
            duplicate_mode="copy",
        )
    )

    assert report.media_file_count == 3
    assert len(report.duplicate_scan_result.exact_groups) == 1
    assert report.decisions_count == 1
    assert report.organize_plan.planned_count == 3
    assert report.rename_dry_run.planned_count == 3
    assert report.has_errors is False


def test_execute_cleanup_workflow_can_apply_organize_and_write_journal(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    report = build_cleanup_workflow_report(
        CleanupWorkflowOptions(source_dirs=(source,), target_root=target)
    )
    journal_path = tmp_path / "journals" / "cleanup-organize.json"
    execution = execute_cleanup_workflow(report, apply_step="organize", journal_path=journal_path)

    assert execution.apply_step == "organize"
    assert execution.organize_result is not None
    assert execution.organize_result.copied_count == 1
    assert journal_path.exists()
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "cleanup-organize"
    assert payload["reversible_entry_count"] == 1


def test_execute_cleanup_workflow_can_apply_rename_and_write_journal(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    report = build_cleanup_workflow_report(
        CleanupWorkflowOptions(source_dirs=(source,), target_root=target)
    )
    journal_path = tmp_path / "journals" / "cleanup-rename.json"
    execution = execute_cleanup_workflow(report, apply_step="rename", journal_path=journal_path)

    assert execution.apply_step == "rename"
    assert execution.rename_result is not None
    assert execution.rename_result.renamed_count == 1
    assert journal_path.exists()
    payload = json.loads(journal_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "cleanup-rename"
    assert payload["reversible_entry_count"] == 1
