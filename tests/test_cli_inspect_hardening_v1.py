from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_inspect import main
from media_manager.core.date_resolver import DateResolution
from media_manager.core.metadata.models import DateCandidate, FileInspection



def test_cli_inspect_json_contains_summary_and_metadata_diagnostics(monkeypatch, capsys, tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.cli_inspect.inspect_media_file",
        lambda path, exiftool_path=None: FileInspection(
            path=path,
            selected_value="2024:08:10 11:12:13",
            selected_source="EXIF:DateTimeOriginal",
            date_candidates=[DateCandidate(source_tag="EXIF:DateTimeOriginal", value="2024:08:10 11:12:13", priority_index=0)],
            file_modified_value="2024-08-10 11:12:14",
            metadata_available=True,
            exiftool_available=True,
            metadata_tag_count=5,
            metadata_error_kind=None,
            error=None,
        ),
    )
    monkeypatch.setattr(
        "media_manager.cli_inspect.resolve_capture_datetime",
        lambda path, inspection=None, exiftool_path=None: DateResolution(
            path=path,
            resolved_datetime=__import__("datetime").datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="test fixture",
            candidates_checked=1,
        ),
    )

    code = main([str(media_file), "--json"])
    captured = capsys.readouterr()

    assert code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["metadata"] == 1
    assert payload["summary"]["warnings"] == 0
    assert payload["files"][0]["metadata_tag_count"] == 5
    assert payload["files"][0]["metadata_error_kind"] is None
