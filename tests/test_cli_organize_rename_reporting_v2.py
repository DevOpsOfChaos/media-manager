from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_organize import main as organize_main
from media_manager.cli_rename import main as rename_main
from media_manager.core.date_resolver import DateResolution


def _resolution(path: Path) -> DateResolution:
    dt = datetime(2024, 8, 10, 11, 12, 13)
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


def test_cli_organize_json_exposes_plan_and_execution_summaries(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    photo = source / "photo.jpg"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr("media_manager.core.organizer.planner.resolve_capture_datetime", lambda path, exiftool_path=None: _resolution(path))

    code = organize_main(["--source", str(source), "--target", str(target), "--apply", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status_summary"] == {"planned": 1}
    assert payload["resolution_source_summary"] == {"metadata": 1}
    assert payload["confidence_summary"] == {"high": 1}
    assert payload["execution"]["outcome_summary"] in ({"copied": 1}, {"moved": 1})
    assert payload["execution"]["reason_summary"] == {"executed organize action": 1}


def test_cli_rename_json_exposes_plan_and_execution_summaries(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    photo = source / "IMG_0001.JPG"
    photo.write_bytes(b"jpg")

    monkeypatch.setattr("media_manager.core.renamer.planner.resolve_capture_datetime", lambda path, exiftool_path=None: _resolution(path))

    code = rename_main(["--source", str(source), "--template", "{date:%Y-%m-%d}_{stem}", "--apply", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["status_summary"] == {"planned": 1}
    assert payload["resolution_source_summary"] == {"metadata": 1}
    assert payload["confidence_summary"] == {"high": 1}
    assert payload["execution"]["status_summary"] == {"renamed": 1}
    assert payload["execution"]["action_summary"] == {"renamed": 1}
    assert payload["execution"]["reason_summary"] == {"rename applied successfully": 1}
