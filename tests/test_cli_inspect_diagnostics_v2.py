from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from media_manager.cli_inspect import main
from media_manager.core.date_resolver import DateResolution
from media_manager.core.metadata.models import DateCandidate, FileInspection


def test_cli_inspect_json_exposes_diagnostic_summaries_and_parseability(monkeypatch, capsys, tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    first.write_bytes(b"1")
    second.write_bytes(b"2")

    def inspect_stub(path: Path, exiftool_path=None) -> FileInspection:
        if path == first:
            return FileInspection(
                path=path,
                selected_value="2024:08:10 11:12:13",
                selected_source="EXIF:DateTimeOriginal",
                date_candidates=[
                    DateCandidate(source_tag="EXIF:DateTimeOriginal", value="2024:08:10 11:12:13", priority_index=0),
                    DateCandidate(source_tag="QuickTime:CreateDate", value="not-a-date", priority_index=1),
                ],
                file_modified_value="2024-08-10 11:12:14",
                metadata_available=True,
                exiftool_available=True,
                metadata_tag_count=4,
                metadata_error_kind=None,
                error=None,
            )
        return FileInspection(
            path=path,
            selected_value="2024-08-10 11:12:14",
            selected_source="file_system:mtime",
            date_candidates=[],
            file_modified_value="2024-08-10 11:12:14",
            metadata_available=False,
            exiftool_available=False,
            metadata_tag_count=0,
            metadata_error_kind="not_found",
            error="exiftool missing",
        )

    def resolve_stub(path: Path, inspection=None, exiftool_path=None) -> DateResolution:
        if path == first:
            dt = datetime(2024, 8, 10, 11, 12, 13)
            return DateResolution(path=path, resolved_datetime=dt, resolved_value="2024-08-10 11:12:13", source_kind="metadata", source_label="EXIF:DateTimeOriginal", confidence="high", timezone_status="naive", reason="from metadata", candidates_checked=2)
        dt = datetime(2024, 8, 10, 11, 12, 14)
        return DateResolution(path=path, resolved_datetime=dt, resolved_value="2024-08-10 11:12:14", source_kind="file_system", source_label="mtime", confidence="low", timezone_status="naive", reason="fallback", candidates_checked=0)

    monkeypatch.setattr("media_manager.cli_inspect.inspect_media_file", inspect_stub)
    monkeypatch.setattr("media_manager.cli_inspect.resolve_capture_datetime", resolve_stub)

    code = main([str(first), str(second), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["summary"]["total_files"] == 2
    assert payload["summary"]["metadata_available_count"] == 1
    assert payload["summary"]["exiftool_available_count"] == 1
    assert payload["summary"]["warning_count"] == 1
    assert payload["summary"]["source_kind_summary"] == {"metadata": 1, "file_system": 1}
    assert payload["summary"]["metadata_error_kind_summary"] == {"not_found": 1}
    assert payload["summary"]["parseable_candidate_count"] == 1
    assert payload["summary"]["unparseable_candidate_count"] == 1
    assert payload["files"][0]["parseable_candidate_count"] == 1
    assert payload["files"][0]["unparseable_candidate_count"] == 1
    assert payload["files"][0]["date_candidates"][1]["parseable"] is False


def test_cli_inspect_text_output_prints_extended_summary(monkeypatch, capsys, tmp_path: Path) -> None:
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
            metadata_tag_count=3,
            metadata_error_kind=None,
            error=None,
        ),
    )
    monkeypatch.setattr(
        "media_manager.cli_inspect.resolve_capture_datetime",
        lambda path, inspection=None, exiftool_path=None: DateResolution(
            path=path,
            resolved_datetime=datetime(2024, 8, 10, 11, 12, 13),
            resolved_value="2024-08-10 11:12:13",
            source_kind="metadata",
            source_label="EXIF:DateTimeOriginal",
            confidence="high",
            timezone_status="naive",
            reason="from metadata",
            candidates_checked=1,
        ),
    )

    code = main([str(media_file)])
    output = capsys.readouterr().out

    assert code == 0
    assert "Inspect summary: total=1" in output
    assert "Resolution sources: metadata=1" in output
    assert "Candidate parseability: parseable=1 | unparseable=0" in output
    assert "Candidate parsing:  parseable=1 | unparseable=0" in output
