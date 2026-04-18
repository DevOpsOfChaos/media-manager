from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_organize import main
from media_manager.core.date_resolver import DateResolution


def test_cli_organize_json_output(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "photo.jpg").write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.organizer.planner.resolve_capture_datetime",
        lambda file_path, exiftool_path=None: DateResolution(
            path=file_path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test fixture",
            candidates_checked=1,
        ),
    )

    code = main(["--source", str(source), "--target", str(tmp_path / "target"), "--json"])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["planned_count"] == 1
    assert payload["entries"][0]["status"] == "planned"
