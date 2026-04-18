from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_rename import main
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


def test_cli_rename_json_output_contains_summary(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["media_file_count"] == 1
    assert payload["planned_count"] == 1


def test_cli_rename_apply_reports_rename_execution(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json", "--apply"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["apply_requested"] is True
    assert payload["execution"]["renamed_count"] == 1
    assert payload["execution"]["entries"][0]["action"] == "renamed"


def test_cli_rename_writes_run_log(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    log_path = tmp_path / "logs" / "rename-run.json"

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda path, exiftool_path=None: _resolution(path),
    )

    exit_code = main(["--source", str(source), "--json", "--run-log", str(log_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    run_log = json.loads(log_path.read_text(encoding="utf-8"))
    assert run_log["command_name"] == "rename"
    assert run_log["apply_requested"] is False
    assert run_log["exit_code"] == 0
    assert run_log["payload"]["planned_count"] == payload["planned_count"]
