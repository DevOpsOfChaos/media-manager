from __future__ import annotations

from datetime import datetime
import re
from typing import Optional


def normalize_offset(date_str: str) -> str:
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"

    if re.match(r".*[+-]\d{4}$", date_str):
        date_str = date_str[:-5] + date_str[-5:-2] + ":" + date_str[-2:]

    return date_str


def parse_exif_date(date_str: str | None) -> Optional[datetime]:
    if not date_str:
        return None

    date_str = normalize_offset(date_str.strip())

    candidates = [
        "%Y:%m:%d %H:%M:%S.%f%z",
        "%Y:%m:%d %H:%M:%S%z",
        "%Y:%m:%d %H:%M:%S.%f",
        "%Y:%m:%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in candidates:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass

    match = re.match(
        r"(\d{4})[:\-](\d{2})[:\-](\d{2})[ T](\d{2}):(\d{2}):(\d{2})",
        date_str,
    )
    if match:
        year, month, day, hour, minute, second = map(int, match.groups())
        try:
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            return None

    return None
