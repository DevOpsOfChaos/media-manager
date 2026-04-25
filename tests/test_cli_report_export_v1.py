from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_cleanup import main as cleanup_main
from media_manager.cli_organize import main as organize_main
from media_manager.cli_rename import main as rename_main
from media_manager.core.date_resolver import DateResolution


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


def test_cli_organize_writes_report_and_review_json(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    report_path = tmp_path / "reports" / "organize.json"
    review_path = tmp_path / "reports" / "organize-review.json"

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = organize_main([
        "--source", str(source),
        "--target", str(target),
        "--report-json", str(report_path),
        "--review-json", str(review_path),
    ])

    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert report["outcome_report"]["command"] == "organize"
    assert review["command"] == "organize"
    assert review["review"]["candidate_count"] == 0


def test_cli_rename_writes_report_and_review_json(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    report_path = tmp_path / "rename.json"
    review_path = tmp_path / "rename-review.json"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = rename_main([
        "--source", str(source),
        "--report-json", str(report_path),
        "--review-json", str(review_path),
    ])

    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert report["outcome_report"]["command"] == "rename"
    assert review["command"] == "rename"
    assert review["outcome_report"]["command"] == "rename"


def test_cli_cleanup_writes_report_and_review_json(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    report_path = tmp_path / "cleanup.json"
    review_path = tmp_path / "cleanup-review.json"

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = cleanup_main([
        "--source", str(source),
        "--target", str(target),
        "--report-json", str(report_path),
        "--review-json", str(review_path),
    ])

    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    assert report["outcome_report"]["command"] == "cleanup"
    assert review["command"] == "cleanup"
    assert review["review"]["candidate_count"] == 0
