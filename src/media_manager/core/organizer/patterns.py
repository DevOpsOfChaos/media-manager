from __future__ import annotations

import re
from pathlib import Path

from media_manager.core.date_resolver import DateResolution

DEFAULT_ORGANIZE_PATTERN = "{year}/{year_month_day}"

_INVALID_SEGMENT_CHARS = re.compile(r'[<>:"\\|?*]')


def _sanitize_segment(value: str) -> str:
    cleaned = _INVALID_SEGMENT_CHARS.sub("_", value.strip())
    if cleaned in {"", ".", ".."}:
        raise ValueError(f"Invalid path segment generated from pattern: {value!r}")
    return cleaned


_MONTH_NAMES_EN = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
_MONTH_NAMES_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

def render_organize_directory(pattern: str, resolution: DateResolution, *, source_root: Path | None = None) -> Path:
    dt = resolution.resolved_datetime
    month_idx = dt.month
    tokens = {
        "year": dt.strftime("%Y"),
        "month": dt.strftime("%m"),
        "month_name": _MONTH_NAMES_EN[month_idx] if 1 <= month_idx <= 12 else dt.strftime("%B"),
        "month_name_de": _MONTH_NAMES_DE[month_idx] if 1 <= month_idx <= 12 else dt.strftime("%B"),
        "day": dt.strftime("%d"),
        "year_month": dt.strftime("%Y-%m"),
        "year_month_day": dt.strftime("%Y-%m-%d"),
        "source_name": source_root.name if source_root is not None else "",
    }
    normalized_pattern = pattern.replace("\\", "/")
    raw_segments = [segment for segment in normalized_pattern.split("/") if segment]
    rendered_segments: list[str] = []
    for segment in raw_segments:
        try:
            rendered = segment.format_map(tokens)
        except KeyError as exc:
            raise ValueError(f"Unknown organize pattern token: {exc.args[0]}") from exc
        rendered_segments.append(_sanitize_segment(rendered))
    if not rendered_segments:
        raise ValueError("Organize pattern produced an empty target directory.")
    return Path(*rendered_segments)
