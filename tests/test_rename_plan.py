from datetime import datetime
from pathlib import Path

from media_manager.rename_plan import (
    RenameBlock,
    blocks_for_template,
    build_filename_preview,
    build_rename_preview,
    template_names,
)


def test_template_names_exposes_expected_templates() -> None:
    names = template_names()

    assert "readable_datetime_original" in names
    assert "year_month_day_time_original" in names
    assert "date_original" in names


def test_blocks_for_template_returns_independent_copy() -> None:
    blocks = blocks_for_template("date_original")
    blocks[0].kind = "year"

    fresh = blocks_for_template("date_original")

    assert fresh[0].kind == "date_iso"


def test_build_filename_preview_with_readable_datetime_blocks() -> None:
    source = Path("IMG_4821.JPG")
    captured_at = datetime(2024, 7, 3, 18, 5, 44)
    blocks = [
        RenameBlock(kind="date_readable", position="prefix"),
        RenameBlock(kind="time_hhmmss", position="prefix"),
        RenameBlock(kind="original_stem", position="suffix"),
    ]

    result = build_filename_preview(source, captured_at, blocks, language="en")

    assert result == "2024 July 03 - 18-05-44 - IMG_4821.JPG"


def test_build_filename_preview_with_german_month_name() -> None:
    source = Path("urlaub.mp4")
    captured_at = datetime(2025, 12, 24, 9, 0, 0)
    blocks = [
        RenameBlock(kind="year", position="prefix"),
        RenameBlock(kind="month_name", position="prefix"),
        RenameBlock(kind="day", position="prefix"),
        RenameBlock(kind="original_stem", position="suffix"),
    ]

    result = build_filename_preview(source, captured_at, blocks, language="de")

    assert result == "2025 - Dezember - 24 - urlaub.mp4"


def test_build_rename_preview_creates_proposed_names_for_each_item() -> None:
    items = [
        (Path("/library/a/IMG_0001.JPG"), datetime(2024, 1, 5, 8, 0, 0)),
        (Path("/library/a/IMG_0002.JPG"), datetime(2024, 1, 5, 8, 5, 0)),
    ]
    blocks = blocks_for_template("date_original")

    preview = build_rename_preview(items, blocks, language="en")

    assert len(preview) == 2
    assert preview[0].proposed_name == "2024-01-05 - IMG_0001.JPG"
    assert preview[1].proposed_name == "2024-01-05 - IMG_0002.JPG"
