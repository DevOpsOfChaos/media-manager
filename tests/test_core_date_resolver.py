from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from media_manager.core.date_resolver import find_filename_datetime, parse_datetime_value, resolve_capture_datetime
from media_manager.core.metadata.models import DateCandidate, FileInspection


def test_parse_datetime_value_supports_exif_iso_and_date_only_inputs() -> None:
    assert parse_datetime_value("2024:08:10 11:12:13") == datetime(2024, 8, 10, 11, 12, 13)
    assert parse_datetime_value("2024-08-10T11:12:13") == datetime(2024, 8, 10, 11, 12, 13)
    assert parse_datetime_value("2024:08:10") == datetime(2024, 8, 10)
    assert parse_datetime_value("20240810") == datetime(2024, 8, 10)


def test_parse_datetime_value_supports_utc_z_suffix() -> None:
    assert parse_datetime_value("2024-08-10T11:12:13Z") == datetime(2024, 8, 10, 11, 12, 13, tzinfo=timezone.utc)


def test_find_filename_datetime_detects_camera_style_names(tmp_path: Path) -> None:
    media_file = tmp_path / "IMG_20240102_123456.jpg"
    media_file.write_bytes(b"jpg")

    match = find_filename_datetime(media_file)

    assert match is not None
    assert match.pattern_name == "compact_datetime"
    assert match.parsed_datetime == datetime(2024, 1, 2, 12, 34, 56)


def test_find_filename_datetime_detects_whatsapp_style_names(tmp_path: Path) -> None:
    media_file = tmp_path / "WhatsApp Image 2024-01-02 at 12.34.56.jpeg"
    media_file.write_bytes(b"jpg")

    match = find_filename_datetime(media_file)

    assert match is not None
    assert match.pattern_name == "whatsapp_datetime"
    assert match.parsed_datetime == datetime(2024, 1, 2, 12, 34, 56)


def test_find_filename_datetime_detects_pixel_style_names_with_milliseconds(tmp_path: Path) -> None:
    media_file = tmp_path / "PXL_20240102_123456789.jpg"
    media_file.write_bytes(b"jpg")

    match = find_filename_datetime(media_file)

    assert match is not None
    assert match.pattern_name == "pixel_datetime_ms"
    assert match.parsed_datetime == datetime(2024, 1, 2, 12, 34, 56)


def test_resolve_capture_datetime_prefers_highest_priority_parseable_metadata_candidate(tmp_path: Path) -> None:
    media_file = tmp_path / "IMG_20240102_123456.jpg"
    media_file.write_bytes(b"jpg")

    inspection = FileInspection(
        path=media_file,
        selected_value="2024:08:10 11:12:13",
        selected_source="EXIF:DateTimeOriginal",
        date_candidates=[
            DateCandidate(source_tag="EXIF:DateTimeOriginal", value="2024:08:10 11:12:13", priority_index=0),
            DateCandidate(source_tag="QuickTime:CreateDate", value="2025:01:01 00:00:00", priority_index=1),
        ],
        file_modified_value="2026-01-01 00:00:00",
        metadata_available=True,
        exiftool_available=True,
        error=None,
    )

    resolution = resolve_capture_datetime(media_file, inspection=inspection)

    assert resolution.source_kind == "metadata"
    assert resolution.source_label == "EXIF:DateTimeOriginal"
    assert resolution.confidence == "high"
    assert resolution.resolved_datetime == datetime(2024, 8, 10, 11, 12, 13)
    assert "ignored 1 lower-priority candidate" in resolution.reason


def test_resolve_capture_datetime_falls_back_to_filename_when_metadata_is_unparseable(tmp_path: Path) -> None:
    media_file = tmp_path / "VID_20240102_123456.mp4"
    media_file.write_bytes(b"mp4")

    inspection = FileInspection(
        path=media_file,
        selected_value="not-a-date",
        selected_source="QuickTime:CreateDate",
        date_candidates=[
            DateCandidate(source_tag="QuickTime:CreateDate", value="not-a-date", priority_index=0),
        ],
        file_modified_value="2026-01-01 00:00:00",
        metadata_available=True,
        exiftool_available=True,
        error=None,
    )

    resolution = resolve_capture_datetime(media_file, inspection=inspection)

    assert resolution.source_kind == "filename"
    assert resolution.source_label in {"compact_datetime", "named_camera_datetime"}
    assert resolution.confidence == "medium"
    assert resolution.resolved_datetime == datetime(2024, 1, 2, 12, 34, 56)
    assert "skipping 1 unparseable metadata candidate" in resolution.reason


def test_resolve_capture_datetime_falls_back_to_file_mtime(tmp_path: Path) -> None:
    media_file = tmp_path / "no-date-here.jpg"
    media_file.write_bytes(b"jpg")

    inspection = FileInspection(
        path=media_file,
        selected_value="2026-01-01 00:00:00",
        selected_source="file_system:mtime",
        date_candidates=[],
        file_modified_value="2026-01-01 00:00:00",
        metadata_available=False,
        exiftool_available=False,
        error=None,
    )

    resolution = resolve_capture_datetime(media_file, inspection=inspection)

    assert resolution.source_kind == "file_system"
    assert resolution.source_label == "mtime"
    assert resolution.confidence == "low"
