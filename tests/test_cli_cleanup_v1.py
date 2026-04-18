from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_cleanup import main
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


def test_cli_cleanup_json_output_contains_sections(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "IMG_20240810_111213.JPG").write_bytes(b"duplicate-bytes")
    (source / "IMG_20240810_111214.JPG").write_bytes(b"other")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = main(["--source", str(source), "--target", str(target), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["scan"]["media_file_count"] == 2
    assert "duplicates" in payload
    assert "organize" in payload
    assert "rename" in payload


def test_cli_cleanup_writes_run_log(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "IMG_20240810_111213.JPG").write_bytes(b"one")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    run_log = tmp_path / "logs" / "cleanup-run.json"
    exit_code = main(["--source", str(source), "--target", str(target), "--run-log", str(run_log), "--json"])

    assert exit_code == 0
    payload = json.loads(run_log.read_text(encoding="utf-8"))
    assert payload["command_name"] == "cleanup"
    assert payload["exit_code"] == 0
