from media_manager.dates import parse_exif_date


def test_parse_exif_with_fraction_and_offset():
    result = parse_exif_date("2024:07:14 16:30:11.123+0200")
    assert result is not None
    assert result.year == 2024
    assert result.month == 7
    assert result.day == 14
    assert result.hour == 16


def test_parse_iso_zulu():
    result = parse_exif_date("2024-07-14T16:30:11Z")
    assert result is not None
    assert result.year == 2024
    assert result.month == 7
    assert result.day == 14


def test_parse_invalid_returns_none():
    assert parse_exif_date("not-a-date") is None
