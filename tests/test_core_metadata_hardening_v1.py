from __future__ import annotations

from pathlib import Path

from media_manager.core.metadata import extract_date_candidates, inspect_media_file



def test_extract_date_candidates_deduplicates_same_priority_values() -> None:
    metadata = {
        "DateTimeOriginal": "2024:08:10 11:12:13",
        "EXIF:DateTimeOriginal": "2024:08:10 11:12:13",
        "QuickTime:CreateDate": "2025:01:01 00:00:00",
    }

    candidates = extract_date_candidates(metadata)

    assert [(item.source_tag, item.value, item.priority_index) for item in candidates] == [
        ("DateTimeOriginal", "2024:08:10 11:12:13", 0),
        ("QuickTime:CreateDate", "2025:01:01 00:00:00", 1),
    ]



def test_inspect_media_file_reports_metadata_diagnostics(monkeypatch, tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")

    monkeypatch.setattr(
        "media_manager.core.metadata.inspect.read_exiftool_metadata",
        lambda file_path, exiftool_path=None, **kwargs: (
            {
                "EXIF:DateTimeOriginal": "2024:08:10 11:12:13",
                "QuickTime:CreateDate": "2025:01:01 00:00:00",
                "OtherTag": "x",
            },
            True,
            None,
            None,
        ),
    )

    inspection = inspect_media_file(media_file)

    assert inspection.metadata_available is True
    assert inspection.exiftool_available is True
    assert inspection.metadata_tag_count == 3
    assert inspection.metadata_error_kind is None
    assert inspection.selected_source == "EXIF:DateTimeOriginal"
    assert len(inspection.date_candidates) == 2
