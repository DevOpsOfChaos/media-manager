from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .exiftool import read_metadata_date

DATE_FORMATS = [
    "%Y:%m:%d %H:%M:%S",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
]


def parse_metadata_datetime(value: str) -> datetime | None:
    raw = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    if len(raw) >= 19:
        truncated = raw[:19]
        for fmt in ["%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            try:
                return datetime.strptime(truncated, fmt)
            except ValueError:
                continue
    return None


def resolve_media_datetime(file_path: Path, exiftool_path: Path | None = None) -> datetime:
    metadata_value = read_metadata_date(file_path, exiftool_path=exiftool_path)
    if metadata_value:
        parsed = parse_metadata_datetime(metadata_value)
        if parsed is not None:
            return parsed

    stat = file_path.stat()
    return datetime.fromtimestamp(stat.st_mtime)
