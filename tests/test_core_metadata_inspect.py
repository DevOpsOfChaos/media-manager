from __future__ import annotations

from pathlib import Path

from media_manager.core.metadata.inspect import extract_date_candidates, inspect_media_file


def test_extract_date_candidates_prefers_priority_order_and_grouped_tags() -> None:
    metadata = {
        "QuickTime:CreateDate": "2024:08:10 11:12:13",
        "EXIF:DateTimeOriginal": "2023:07:09 08:07:06",
        "File:FileModifyDate": "2025:01:02 03:04:05",
    }

    candidates = extract_date_candidates(metadata)

    assert [item.source_tag for item in candidates] == [
        "EXIF:DateTimeOriginal",
        "QuickTime:CreateDate",
        "File:FileModifyDate",
    ]


def test_inspect_media_file_falls_back_to_file_mtime_when_no_metadata(monkeypatch, tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.metadata.inspect._read_exiftool_metadata",
        lambda file_path, exiftool_path=None: (None, False, None),
    )

    inspection = inspect_media_file(media_file)

    assert inspection.path == media_file
    assert inspection.selected_source == "file_system:mtime"
    assert inspection.selected_value == inspection.file_modified_value
    assert inspection.date_candidates == []
    assert inspection.exiftool_available is False


def test_inspect_media_file_uses_first_candidate_from_metadata(monkeypatch, tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.metadata.inspect._read_exiftool_metadata",
        lambda file_path, exiftool_path=None: (
            {
                "QuickTime:CreateDate": "2024:08:10 11:12:13",
                "EXIF:DateTimeOriginal": "2023:07:09 08:07:06",
            },
            True,
            None,
        ),
    )

    inspection = inspect_media_file(media_file)

    assert inspection.selected_source == "EXIF:DateTimeOriginal"
    assert inspection.selected_value == "2023:07:09 08:07:06"
    assert inspection.metadata_available is True
    assert inspection.exiftool_available is True
    assert [item.source_tag for item in inspection.date_candidates] == [
        "EXIF:DateTimeOriginal",
        "QuickTime:CreateDate",
    ]
