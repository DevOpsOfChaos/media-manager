from datetime import datetime

from media_manager.dates import parse_metadata_datetime


def test_parse_standard_exif_datetime() -> None:
    parsed = parse_metadata_datetime("2024:07:18 13:45:09")
    assert parsed == datetime(2024, 7, 18, 13, 45, 9)


def test_parse_iso_datetime() -> None:
    parsed = parse_metadata_datetime("2024-07-18T13:45:09")
    assert parsed == datetime(2024, 7, 18, 13, 45, 9)


def test_parse_with_trailing_timezone_suffix_by_truncation() -> None:
    parsed = parse_metadata_datetime("2024:07:18 13:45:09+02:00")
    assert parsed == datetime(2024, 7, 18, 13, 45, 9, tzinfo=parsed.tzinfo) or parsed == datetime(2024, 7, 18, 13, 45, 9)
