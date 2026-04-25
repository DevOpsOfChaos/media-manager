from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_cleanup import main as cleanup_main
from media_manager.cli_organize import main as organize_main
from media_manager.cli_rename import main as rename_main
from media_manager.core.date_resolver import DateResolution
from media_manager.core.review_report import build_review_export


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


class _Entry:
    def __init__(self, source_path: Path, target_path: Path, status: str, reason: str) -> None:
        self.source_path = source_path
        self.target_path = target_path
        self.status = status
        self.reason = reason
        self.group_kind = "single"
        self.associated_paths = ()
        self.association_warnings = ()


def test_review_export_summarizes_conflict_and_error_entries(tmp_path: Path) -> None:
    first = _Entry(tmp_path / "a.jpg", tmp_path / "target/a.jpg", "conflict", "target exists")
    second = _Entry(tmp_path / "b.jpg", tmp_path / "target/b.jpg", "error", "date failed")

    payload = build_review_export({"organize": [first], "rename": [second]})

    assert payload["candidate_count"] == 2
    assert payload["section_summary"] == {"organize": 1, "rename": 1}
    assert payload["reason_summary"] == {"conflict": 1, "error": 1}
    assert payload["candidates"][0]["section"] == "organize"
    assert payload["candidates"][0]["review_reasons"] == ["conflict"]


def test_cli_organize_json_includes_review_export_for_conflict(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"new")
    (target / "2024" / "2024-08-10").mkdir(parents=True)
    (target / "2024" / "2024-08-10" / "photo.jpg").write_bytes(b"existing")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = organize_main(["--source", str(source), "--target", str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["review"]["candidate_count"] == 1
    assert payload["review"]["reason_summary"] == {"conflict": 1}
    assert payload["review"]["candidates"][0]["section"] == "organize"
    assert payload["review"]["candidates"][0]["source_path"].endswith("photo.jpg")


def test_cli_rename_json_includes_review_export_for_conflict(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"new")
    (source / "2024-08-10_11-12-13_IMG_0001.JPG").write_bytes(b"existing")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = rename_main(["--source", str(source), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["review"]["candidate_count"] == 1
    assert payload["review"]["reason_summary"] == {"conflict": 1}
    assert payload["review"]["candidates"][0]["section"] == "rename"


def test_cli_cleanup_review_block_includes_candidate_details(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"new")
    (target / "2024" / "2024-08-10").mkdir(parents=True)
    (target / "2024" / "2024-08-10" / "photo.jpg").write_bytes(b"existing")

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
    assert payload["review"]["candidate_count"] >= 1
    assert payload["review"]["candidates"]
    assert payload["review"]["candidates"][0]["review_reasons"]
