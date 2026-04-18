
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


def test_cli_cleanup_json_output_contains_section_summaries(monkeypatch, capsys, tmp_path: Path) -> None:
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

    code = main(
        [
            "--source",
            str(source_a),
            "--source",
            str(source_b),
            "--target",
            str(tmp_path / "target"),
            "--duplicate-policy",
            "first",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["duplicates"]["exact_groups"] == 1
    assert payload["duplicates"]["decisions"] == 1
    assert payload["organize"]["planned_count"] == 2
    assert payload["rename"]["planned_count"] == 2


def test_cli_cleanup_writes_run_log(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"solo")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    log_path = tmp_path / "logs" / "cleanup-run.json"
    code = main(
        [
            "--source",
            str(source),
            "--target",
            str(tmp_path / "target"),
            "--run-log",
            str(log_path),
        ]
    )

    assert code == 0
    assert log_path.exists()
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "cleanup"
    assert payload["apply_requested"] is False
