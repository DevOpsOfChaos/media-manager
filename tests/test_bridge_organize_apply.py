from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_organize_apply import cmd_apply


def _make_options(source: Path, target: Path, **overrides) -> dict:
    return {
        "source_dirs": [str(source)],
        "target_root": str(target),
        "pattern": "{year}/{year_month_day}",
        "recursive": True,
        "operation_mode": "copy",
        **overrides,
    }


def test_apply_copies_files(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    jpg = source / "photo.jpg"
    jpg.write_bytes(b"jpg-content")

    from media_manager.core.date_resolver import DateResolution
    from datetime import datetime
    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: DateResolution(
            path=file_path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test",
            candidates_checked=1,
        ),
    )

    options = _make_options(source, target)
    fake_stdin = StringIO(json.dumps(options))
    with mock.patch.object(sys, "stdin", fake_stdin):
        exit_code = cmd_apply()

    assert exit_code == 0
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_apply_moves_files(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    jpg = source / "photo.jpg"
    jpg.write_bytes(b"jpg-content")

    from media_manager.core.date_resolver import DateResolution
    from datetime import datetime
    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: DateResolution(
            path=file_path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test",
            candidates_checked=1,
        ),
    )

    options = _make_options(source, target, operation_mode="move")
    fake_stdin = StringIO(json.dumps(options))
    with mock.patch.object(sys, "stdin", fake_stdin):
        exit_code = cmd_apply()

    assert exit_code == 0
    assert not jpg.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()


def test_apply_includes_journal_entries(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    jpg = source / "photo.jpg"
    jpg.write_bytes(b"jpg-content")

    from media_manager.core.date_resolver import DateResolution
    from datetime import datetime
    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: DateResolution(
            path=file_path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test",
            candidates_checked=1,
        ),
    )

    options = _make_options(source, target)
    fake_stdin = StringIO(json.dumps(options))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "apply"
    assert output["dry_run"] is False
    assert output["executed_count"] == 1
    assert len(output["journal_entries"]) >= 1
    je = output["journal_entries"][0]
    assert je["reversible"] is True
    assert je["undo_action"] in ("delete_target", "move_back")


def test_apply_with_associated_files(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    jpg = source / "photo.jpg"
    xmp = source / "photo.xmp"
    jpg.write_bytes(b"jpg-content")
    xmp.write_bytes(b"xmp-content")

    from media_manager.core.date_resolver import DateResolution
    from datetime import datetime
    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None, **kwargs: DateResolution(
            path=file_path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test",
            candidates_checked=1,
        ),
    )

    options = _make_options(source, target, include_associated_files=True, operation_mode="move")
    fake_stdin = StringIO(json.dumps(options))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    assert not jpg.exists()
    assert not xmp.exists()
    assert (target / "2024" / "2024-08-10" / "photo.jpg").exists()
    assert (target / "2024" / "2024-08-10" / "photo.xmp").exists()
    output = json.loads(fake_stdout.getvalue())
    assert len(output["journal_entries"]) >= 2  # one per member
