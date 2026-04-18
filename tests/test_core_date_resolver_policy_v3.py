from __future__ import annotations

from datetime import datetime
from pathlib import Path

from media_manager.core.date_resolver import resolve_capture_datetime
from media_manager.core.metadata.models import DateCandidate, FileInspection


def test_resolve_capture_datetime_marks_metadata_conflict_when_parseable_values_disagree(tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    inspection = FileInspection(
        path=media_file,
        selected_value="2024:08:10 11:12:13",
        selected_source="EXIF:DateTimeOriginal",
        date_candidates=[
            DateCandidate(source_tag="EXIF:DateTimeOriginal", value="2024:08:10 11:12:13", priority_index=0),
            DateCandidate(source_tag="QuickTime:CreateDate", value="2024:08:10 11:12:14", priority_index=1),
            DateCandidate(source_tag="File:FileModifyDate", value="not-a-date", priority_index=2),
        ],
        file_modified_value="2024-08-10 11:12:15",
        metadata_available=True,
        exiftool_available=True,
    )

    resolution = resolve_capture_datetime(media_file, inspection=inspection)

    assert resolution.source_kind == "metadata"
    assert resolution.metadata_conflict is True
    assert resolution.parseable_candidate_count == 2
    assert resolution.unparseable_candidate_count == 1
    assert resolution.decision_policy == "highest_priority_parseable_metadata"
    assert "disagreed across 2 distinct values" in resolution.reason


def test_resolve_capture_datetime_marks_metadata_agreement_when_parseable_values_match(tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    inspection = FileInspection(
        path=media_file,
        selected_value="2024:08:10 11:12:13",
        selected_source="EXIF:DateTimeOriginal",
        date_candidates=[
            DateCandidate(source_tag="EXIF:DateTimeOriginal", value="2024:08:10 11:12:13", priority_index=0),
            DateCandidate(source_tag="QuickTime:CreateDate", value="2024:08:10 11:12:13", priority_index=1),
        ],
        file_modified_value="2024-08-10 11:12:15",
        metadata_available=True,
        exiftool_available=True,
    )

    resolution = resolve_capture_datetime(media_file, inspection=inspection)

    assert resolution.metadata_conflict is False
    assert resolution.parseable_candidate_count == 2
    assert resolution.unparseable_candidate_count == 0
    assert "agreed with the selected value" in resolution.reason
