from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_cleanup import main as cleanup_main
from media_manager.cli_organize import main as organize_main
from media_manager.cli_rename import main as rename_main
from media_manager.core.date_resolver import DateResolution
from media_manager.core.scanner import ScanOptions, scan_media_sources
from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates


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


def test_scanner_include_and_exclude_patterns_filter_media_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "keep.jpg").write_bytes(b"keep")
    (source / "drop.jpg").write_bytes(b"drop")
    (source / "movie.mov").write_bytes(b"movie")

    summary = scan_media_sources(
        ScanOptions(
            source_dirs=(source,),
            include_patterns=("*.jpg",),
            exclude_patterns=("drop*",),
        )
    )

    assert [item.path.name for item in summary.files] == ["keep.jpg"]
    assert summary.skipped_filtered_files == 2


def test_duplicate_scan_respects_include_and_exclude_patterns(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "keep_a.jpg").write_bytes(b"same")
    (source / "keep_b.jpg").write_bytes(b"same")
    (source / "drop_a.jpg").write_bytes(b"same")

    result = scan_exact_duplicates(
        DuplicateScanConfig(
            source_dirs=[source],
            include_patterns=("keep*",),
        )
    )

    assert result.scanned_files == 2
    assert result.skipped_filtered_files == 1
    assert len(result.exact_groups) == 1


def test_cli_organize_json_reports_include_exclude_patterns(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "keep.jpg").write_bytes(b"keep")
    (source / "drop.mov").write_bytes(b"drop")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = organize_main([
        "--source", str(source),
        "--target", str(target),
        "--include-pattern", "*.jpg",
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["include_patterns"] == ["*.jpg"]
    assert payload["exclude_patterns"] == []
    assert payload["media_file_count"] == 1
    assert payload["skipped_filtered_files"] == 1


def test_cli_rename_json_reports_include_exclude_patterns(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "keep.jpg").write_bytes(b"keep")
    (source / "drop.mov").write_bytes(b"drop")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = rename_main([
        "--source", str(source),
        "--exclude-pattern", "*.mov",
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["include_patterns"] == []
    assert payload["exclude_patterns"] == ["*.mov"]
    assert payload["media_file_count"] == 1
    assert payload["skipped_filtered_files"] == 1


def test_cli_cleanup_json_reports_filter_counts(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "keep_a.jpg").write_bytes(b"same")
    (source / "keep_b.jpg").write_bytes(b"same")
    (source / "drop.mov").write_bytes(b"drop")

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
        "--include-pattern", "keep*",
        "--json",
    ])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["include_patterns"] == ["keep*"]
    assert payload["scan"]["media_file_count"] == 2
    assert payload["scan"]["skipped_filtered_files"] == 1
    assert payload["duplicates"]["skipped_filtered_files"] == 1
