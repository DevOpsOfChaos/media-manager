from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_inspect import main


def test_cli_inspect_json_includes_summary_and_candidate_parseability(monkeypatch, capsys, tmp_path: Path) -> None:
    media_file = tmp_path / "IMG_20240102_123456.jpg"
    media_file.write_bytes(b"jpg")

    inspection = SimpleNamespace(
        path=media_file,
        selected_value="2024:01:02 12:34:56",
        selected_source="EXIF:DateTimeOriginal",
        file_modified_value="2024-01-03 00:00:00",
        metadata_available=True,
        exiftool_available=True,
        metadata_tag_count=2,
        metadata_error_kind=None,
        error=None,
        date_candidates=[
            SimpleNamespace(source_tag="EXIF:DateTimeOriginal", value="2024:01:02 12:34:56", priority_index=0),
            SimpleNamespace(source_tag="QuickTime:CreateDate", value="not-a-date", priority_index=1),
        ],
    )
    resolution = SimpleNamespace(
        resolved_value="2024-01-02 12:34:56",
        source_kind="metadata",
        source_label="EXIF:DateTimeOriginal",
        confidence="high",
        timezone_status="naive",
        reason="Selected metadata candidate.",
        candidates_checked=2,
        decision_policy="metadata_first_parseable",
        metadata_conflict=False,
        parseable_candidate_count=1,
        unparseable_candidate_count=1,
    )

    monkeypatch.setattr("media_manager.cli_inspect.inspect_media_file", lambda path, exiftool_path=None: inspection)
    monkeypatch.setattr("media_manager.cli_inspect.resolve_capture_datetime", lambda path, inspection=None, exiftool_path=None: resolution)

    code = main([str(media_file), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["summary"]["total_files"] == 1
    assert payload["summary"]["metadata"] == 1
    assert payload["summary"]["parseable_candidate_count"] == 1
    assert payload["summary"]["unparseable_candidate_count"] == 1
    assert payload["files"][0]["date_candidates"][0]["parseable"] is True
    assert payload["files"][0]["date_candidates"][1]["parseable"] is False
