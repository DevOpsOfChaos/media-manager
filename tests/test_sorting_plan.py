from datetime import datetime
from pathlib import Path

from media_manager.sorting_plan import (
    DEFAULT_SORT_LEVELS,
    SortLevel,
    build_relative_sort_directory,
    build_sort_preview,
)


def test_build_relative_sort_directory_with_default_levels() -> None:
    captured_at = datetime(2024, 7, 3, 18, 30, 0)

    result = build_relative_sort_directory(captured_at, DEFAULT_SORT_LEVELS, language="en")

    assert result == Path("2024") / "07" / "03"


def test_build_relative_sort_directory_with_month_name_in_german() -> None:
    captured_at = datetime(2025, 12, 24, 9, 0, 0)
    levels = [
        SortLevel(kind="year", style="yyyy"),
        SortLevel(kind="month", style="name"),
    ]

    result = build_relative_sort_directory(captured_at, levels, language="de")

    assert result == Path("2025") / "Dezember"


def test_build_sort_preview_creates_relative_targets_for_each_item() -> None:
    items = [
        (Path("/library/a/img_001.jpg"), datetime(2024, 1, 5, 8, 0, 0)),
        (Path("/library/a/img_002.jpg"), datetime(2024, 1, 5, 8, 5, 0)),
    ]
    levels = [
        SortLevel(kind="year", style="yyyy"),
        SortLevel(kind="month", style="yyyy-mm"),
        SortLevel(kind="day", style="dd"),
    ]

    preview = build_sort_preview(items, levels, language="en")

    assert len(preview) == 2
    assert preview[0].relative_directory == Path("2024") / "2024-01" / "05"
    assert preview[1].relative_directory == Path("2024") / "2024-01" / "05"
