from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class RenameBlock:
    kind: str
    position: str = "prefix"


@dataclass(slots=True)
class RenamePreviewItem:
    source_path: Path
    captured_at: datetime
    proposed_name: str


TEMPLATE_LIBRARY: dict[str, list[RenameBlock]] = {
    "readable_datetime_original": [
        RenameBlock(kind="date_readable", position="prefix"),
        RenameBlock(kind="time_hhmmss", position="prefix"),
        RenameBlock(kind="original_stem", position="suffix"),
    ],
    "year_month_day_time_original": [
        RenameBlock(kind="year", position="prefix"),
        RenameBlock(kind="month_name", position="prefix"),
        RenameBlock(kind="day", position="prefix"),
        RenameBlock(kind="time_hhmmss", position="prefix"),
        RenameBlock(kind="original_stem", position="suffix"),
    ],
    "date_original": [
        RenameBlock(kind="date_iso", position="prefix"),
        RenameBlock(kind="original_stem", position="suffix"),
    ],
}

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


def template_names() -> list[str]:
    return list(TEMPLATE_LIBRARY.keys())


def blocks_for_template(template_name: str) -> list[RenameBlock]:
    if template_name not in TEMPLATE_LIBRARY:
        raise ValueError(f"Unknown rename template: {template_name}")
    return [RenameBlock(block.kind, block.position) for block in TEMPLATE_LIBRARY[template_name]]


def format_rename_block(
    block: RenameBlock,
    captured_at: datetime,
    source_path: Path,
    language: str = "en",
) -> str:
    if block.kind == "original_stem":
        return source_path.stem
    if block.kind == "year":
        return captured_at.strftime("%Y")
    if block.kind == "day":
        return captured_at.strftime("%d")
    if block.kind == "month_name":
        month_names = MONTH_NAMES_DE if language == "de" else MONTH_NAMES_EN
        return month_names[captured_at.month]
    if block.kind == "date_iso":
        return captured_at.strftime("%Y-%m-%d")
    if block.kind == "date_readable":
        month_names = MONTH_NAMES_DE if language == "de" else MONTH_NAMES_EN
        return f"{captured_at.year} {month_names[captured_at.month]} {captured_at.day:02d}"
    if block.kind == "time_hhmmss":
        return captured_at.strftime("%H-%M-%S")
    raise ValueError(f"Unsupported rename block kind: {block.kind}")


def build_filename_preview(
    source_path: Path,
    captured_at: datetime,
    blocks: Iterable[RenameBlock],
    language: str = "en",
    separator: str = " - ",
) -> str:
    prefix_parts: list[str] = []
    suffix_parts: list[str] = []

    for block in blocks:
        part = format_rename_block(block, captured_at, source_path, language=language).strip()
        if not part:
            continue
        if block.position == "suffix":
            suffix_parts.append(part)
        else:
            prefix_parts.append(part)

    ordered_parts = prefix_parts + suffix_parts
    base_name = separator.join(ordered_parts).strip()
    if not base_name:
        base_name = source_path.stem
    return f"{base_name}{source_path.suffix}"


def build_rename_preview(
    items: Iterable[tuple[Path, datetime]],
    blocks: Iterable[RenameBlock],
    language: str = "en",
    separator: str = " - ",
) -> list[RenamePreviewItem]:
    preview: list[RenamePreviewItem] = []
    block_list = list(blocks)
    for source_path, captured_at in items:
        preview.append(
            RenamePreviewItem(
                source_path=source_path,
                captured_at=captured_at,
                proposed_name=build_filename_preview(
                    source_path,
                    captured_at,
                    block_list,
                    language=language,
                    separator=separator,
                ),
            )
        )
    return preview
