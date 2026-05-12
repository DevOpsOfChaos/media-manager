"""Tests for bridge_organize_preview — read-only organize preview only."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path

from media_manager.bridge_organize_preview import cmd_preview, main


def _resolution(path: Path, dt: datetime):
    from media_manager.core.date_resolver import DateResolution
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


def test_preview_empty_source_dirs() -> None:
    """Rejects missing source_dirs with error."""
    old_stdin = sys.stdin
    sys.stdin = StringIO(json.dumps({"target_root": "/tmp/target"}))
    try:
        exit_code = cmd_preview()
        assert exit_code == 1
    finally:
        sys.stdin = old_stdin


def test_preview_empty_target_root() -> None:
    """Rejects missing target_root with error."""
    old_stdin = sys.stdin
    sys.stdin = StringIO(json.dumps({"source_dirs": ["/tmp/src"]}))
    try:
        exit_code = cmd_preview()
        assert exit_code == 1
    finally:
        sys.stdin = old_stdin


def test_preview_returns_dry_run_marker(monkeypatch, tmp_path: Path) -> None:
    """Preview result is marked as dry_run=True, kind=preview."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(
            file_path, datetime(2024, 8, 10, 11, 12, 13)
        ),
    )

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        assert output["dry_run"] is True
        assert output["media_file_count"] == 1
        assert output["planned_count"] == 1
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_includes_outcome_report(monkeypatch, tmp_path: Path) -> None:
    """Preview includes safe_to_apply and outcome_report."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(
            file_path, datetime(2024, 8, 10, 11, 12, 13)
        ),
    )

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        report = output["outcome_report"]
        assert report["command"] == "organize_preview"
        assert report["phase"] == "plan"
        assert "safe_to_apply" in report
        assert "needs_review" in report
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_never_modifies_files(monkeypatch, tmp_path: Path) -> None:
    """Source files remain unchanged after preview."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"original-content")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(
            file_path, datetime(2024, 8, 10, 11, 12, 13)
        ),
    )

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        cmd_preview()
        # Source file must remain untouched
        assert photo.read_bytes() == b"original-content"
        # Target should NOT have been created (dry-run only reads)
        target_files = list(target.rglob("*"))
        assert len(target_files) == 0, f"Dry-run must not create files. Found: {target_files}"
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_entries_have_expected_fields(monkeypatch, tmp_path: Path) -> None:
    """Each entry has source_path, target_path, status, reason, etc."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(
            file_path, datetime(2024, 8, 10, 11, 12, 13)
        ),
    )

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        cmd_preview()
        output = json.loads(sys.stdout.getvalue())
        entries = output["entries"]
        assert len(entries) == 1
        e = entries[0]
        assert "source_path" in e
        assert "target_path" in e
        assert e["status"] == "planned"
        assert e["operation_mode"] == "copy"
        assert e["group_id"] is None
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_handles_invalid_json() -> None:
    """Invalid JSON input returns error exit code."""
    old_stdin = sys.stdin
    sys.stdin = StringIO("not valid json {{{")
    try:
        exit_code = cmd_preview()
        assert exit_code == 1
    finally:
        sys.stdin = old_stdin


def test_preview_handles_nonexistent_source(monkeypatch, tmp_path: Path) -> None:
    """Preview handles non-existent source gracefully (missing_sources)."""
    source = tmp_path / "does_not_exist"
    target = tmp_path / "target"
    target.mkdir()

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        # Missing sources are reported, not fatal
        assert "scan_summary" in output
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_main_returns_exit_code(monkeypatch, tmp_path: Path) -> None:
    """main() returns exit code, does not raise."""
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(
            file_path, datetime(2024, 8, 10, 11, 12, 13)
        ),
    )

    options = {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "operation_mode": "copy",
    }

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps(options))
    sys.stdout = StringIO()
    try:
        result = main()
        assert result == 0
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
