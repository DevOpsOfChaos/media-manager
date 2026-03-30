from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

MONTH_NAMES_EN = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

MONTH_NAMES_DE = {
    1: "Januar",
    2: "Februar",
    3: "März",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}


@dataclass(slots=True)
class SortLevel:
    kind: str
    style: str


@dataclass(slots=True)
class SortPreviewItem:
    source_path: Path
    captured_at: datetime
    relative_directory: Path


DEFAULT_SORT_LEVELS = [
    SortLevel(kind="year", style="yyyy"),
    SortLevel(kind="month", style="mm"),
    SortLevel(kind="day", style="dd"),
]


def format_sort_level(level: SortLevel, captured_at: datetime, language: str = "en") -> str:
    if level.kind == "year":
        if level.style == "yy":
            return captured_at.strftime("%y")
        return captured_at.strftime("%Y")

    if level.kind == "month":
        if level.style == "name":
            month_names = MONTH_NAMES_DE if language == "de" else MONTH_NAMES_EN
            return month_names[captured_at.month]
        if level.style == "yyyy-mm":
            return captured_at.strftime("%Y-%m")
        return captured_at.strftime("%m")

    if level.kind == "day":
        if level.style == "yyyy-mm-dd":
            return captured_at.strftime("%Y-%m-%d")
        return captured_at.strftime("%d")

    raise ValueError(f"Unsupported sort level: {level.kind}:{level.style}")


def build_relative_sort_directory(
    captured_at: datetime,
    levels: Iterable[SortLevel],
    language: str = "en",
) -> Path:
    parts = [format_sort_level(level, captured_at, language=language) for level in levels]
    return Path(*parts)


def build_sort_preview(
    items: Iterable[tuple[Path, datetime]],
    levels: Iterable[SortLevel],
    language: str = "en",
) -> list[SortPreviewItem]:
    preview: list[SortPreviewItem] = []
    level_list = list(levels)
    for source_path, captured_at in items:
        preview.append(
            SortPreviewItem(
                source_path=source_path,
                captured_at=captured_at,
                relative_directory=build_relative_sort_directory(captured_at, level_list, language=language),
            )
        )
    return preview
