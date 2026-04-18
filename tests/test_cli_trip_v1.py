from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_trip import main
from media_manager.core.date_resolver import DateResolution


def _resolution(path: Path) -> DateResolution:
    dt = datetime(2025, 8, 10, 11, 12, 13)
    return DateResolution(
        path=path,
        resolved_datetime=dt,
        resolved_value="2025-08-10 11:12:13",
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="test fixture",
        candidates_checked=1,
    )


def test_cli_trip_json_output_contains_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(tmp_path / "collections"),
        "--label", "Italy_2025",
        "--start", "2025-08-01",
        "--end", "2025-08-14",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["selected_count"] == 1
    assert payload["planned_count"] == 1
    assert payload["mode"] == "link"


def test_cli_trip_apply_copy_reports_execution(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(tmp_path / "collections"),
        "--label", "Italy_2025",
        "--start", "2025-08-01",
        "--end", "2025-08-14",
        "--copy",
        "--apply",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["executed_count"] == 1
    assert payload["execution"]["copied_count"] == 1
    assert payload["execution"]["entries"][0]["outcome"] == "copied"


def test_cli_trip_writes_run_log(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    run_log = tmp_path / "logs" / "trip-run.json"

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(tmp_path / "collections"),
        "--label", "Italy_2025",
        "--start", "2025-08-01",
        "--end", "2025-08-14",
        "--run-log", str(run_log),
    ])

    assert exit_code == 0
    assert run_log.exists()
    payload = json.loads(run_log.read_text(encoding="utf-8"))
    assert payload["command_name"] == "trip"
    assert payload["payload"]["selected_count"] == 1


def test_cli_trip_apply_writes_execution_journal(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "Phone"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")
    journal = tmp_path / "journals" / "trip-execution.json"

    monkeypatch.setattr(
        "media_manager.core.workflows.trip.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(tmp_path / "collections"),
        "--label", "Italy_2025",
        "--start", "2025-08-01",
        "--end", "2025-08-14",
        "--copy",
        "--apply",
        "--journal", str(journal),
    ])

    assert exit_code == 0
    payload = json.loads(journal.read_text(encoding="utf-8"))
    assert payload["command_name"] == "trip"
    assert payload["entries"][0]["outcome"] == "copied"
    assert payload["entries"][0]["undo_action"] == "delete_target"
