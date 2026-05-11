from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_duplicates import main as duplicates_main
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


def _single_run_dir(root: Path) -> Path:
    run_dirs = [path for path in root.iterdir() if path.is_dir()]
    assert len(run_dirs) == 1
    return run_dirs[0]


def test_organize_writes_structured_run_artifacts(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    run_root = tmp_path / "runs"
    source.mkdir()
    target.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path),
    )

    exit_code = organize_main(["--source", str(source), "--target", str(target), "--run-dir", str(run_root)])

    assert exit_code == 0
    run_dir = _single_run_dir(run_root)
    assert run_dir.name.endswith("-organize-preview")
    assert (run_dir / "command.json").is_file()
    assert (run_dir / "report.json").is_file()
    assert (run_dir / "review.json").is_file()
    assert (run_dir / "summary.txt").is_file()
    assert not (run_dir / "journal.json").exists()

    command = json.loads((run_dir / "command.json").read_text(encoding="utf-8"))
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    review = json.loads((run_dir / "review.json").read_text(encoding="utf-8"))
    summary = (run_dir / "summary.txt").read_text(encoding="utf-8")

    assert command["command"] == "organize"
    assert report["outcome_report"]["command"] == "organize"
    assert review["command"] == "organize"
    assert "Command: organize" in summary


def test_rename_apply_writes_journal_in_run_artifacts(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    run_root = tmp_path / "runs"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.renamer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: _resolution(file_path),
    )

    exit_code = rename_main(["--source", str(source), "--run-dir", str(run_root), "--apply"])

    assert exit_code == 0
    run_dir = _single_run_dir(run_root)
    assert run_dir.name.endswith("-rename-apply")
    journal = json.loads((run_dir / "journal.json").read_text(encoding="utf-8"))
    assert journal["command_name"] == "rename"
    assert journal["apply_requested"] is True
    assert journal["entries"]


def test_duplicates_writes_structured_run_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source"
    run_root = tmp_path / "runs"
    source.mkdir()
    (source / "a.mp4").write_text("same", encoding="utf-8")
    (source / "b.mp4").write_text("same", encoding="utf-8")

    exit_code = duplicates_main(["--source", str(source), "--media-kind", "video", "--run-dir", str(run_root)])

    assert exit_code == 0
    run_dir = _single_run_dir(run_root)
    assert run_dir.name.endswith("-duplicates-preview")
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    review = json.loads((run_dir / "review.json").read_text(encoding="utf-8"))
    assert report["summary"]["video_file_count"] == 2
    assert review["command"] == "duplicates"
    assert review["review"]["candidate_count"] >= 1
