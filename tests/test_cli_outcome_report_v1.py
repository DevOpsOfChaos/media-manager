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


def test_cli_organize_json_includes_outcome_report(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = organize_main(["--source", str(source), "--target", str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["outcome_report"]["command"] == "organize"
    assert payload["outcome_report"]["status"] == "ready"
    assert payload["outcome_report"]["safe_to_apply"] is True
    assert payload["outcome_report"]["counts"]["planned"] == 1


def test_cli_rename_json_includes_plan_and_preview_outcome_reports(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = rename_main(["--source", str(source), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["outcome_report"]["command"] == "rename"
    assert payload["outcome_report"]["status"] == "ready"
    assert payload["execution"]["outcome_report"]["phase"] == "preview"
    assert payload["execution"]["outcome_report"]["status"] == "preview_ready"


def test_cli_cleanup_json_includes_workflow_outcome_report(monkeypatch, tmp_path: Path, capsys) -> None:
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

    exit_code = cleanup_main(["--source", str(source), "--target", str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["outcome_report"]["command"] == "cleanup"
    assert payload["outcome_report"]["status"] == "ready"
    assert payload["outcome_report"]["sections"]["organize"]["command"] == "cleanup.organize"
    assert payload["outcome_report"]["sections"]["rename"]["command"] == "cleanup.rename"
