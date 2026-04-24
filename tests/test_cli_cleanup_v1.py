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


def test_cli_cleanup_can_apply_organize_and_emit_execution_json(monkeypatch, tmp_path: Path, capsys) -> None:
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

    exit_code = main([
        "--source", str(source),
        "--target", str(target),
        "--apply-organize",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["apply_step"] == "organize"
    assert payload["execution"]["copied_count"] == 1


def test_cli_cleanup_can_apply_rename_and_write_journal(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "IMG_0001.JPG").write_bytes(b"jpg")
    journal_path = tmp_path / "journals" / "cleanup-rename.json"

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(target),
        "--apply-rename",
        "--journal", str(journal_path),
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["apply_step"] == "rename"
    assert payload["execution"]["journal_path"] == str(journal_path)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert journal["command_name"] == "cleanup-rename"


def test_cli_cleanup_apply_organize_can_consolidate_leftovers(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    nested = source / "nested"
    target = tmp_path / "target"
    source.mkdir()
    nested.mkdir()
    target.mkdir()
    (nested / "photo.jpg").write_bytes(b"jpg")
    (nested / "notes.txt").write_text("note", encoding="utf-8")
    journal_path = tmp_path / "journals" / "cleanup-organize.json"

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )
    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: _resolution(file_path),
    )

    exit_code = main([
        "--source", str(source),
        "--target", str(target),
        "--apply-organize",
        "--leftover-mode", "consolidate",
        "--journal", str(journal_path),
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["execution"]["apply_step"] == "organize"
    assert payload["execution"]["leftover"]["file_count"] == 2
    assert payload["execution"]["leftover"]["removed_empty_directory_count"] == 1
    assert (source / "_remaining_files" / "photo.jpg").exists()
    assert (source / "_remaining_files" / "notes.txt").exists()
    assert not nested.exists()

    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    assert journal["command_name"] == "cleanup-organize"
    assert journal["entry_count"] == 3
    assert journal["reversible_entry_count"] == 3


def test_cli_cleanup_rejects_leftover_mode_without_apply_organize(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    try:
        main([
            "--source", str(source),
            "--target", str(target),
            "--leftover-mode", "consolidate",
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("Expected argparse to reject leftover consolidation without --apply-organize.")


def test_cli_cleanup_rejects_journal_without_apply(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    try:
        main([
            "--source", str(source),
            "--target", str(target),
            "--journal", str(tmp_path / "journal.json"),
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover
        raise AssertionError("Expected argparse to reject --journal without an apply step.")
