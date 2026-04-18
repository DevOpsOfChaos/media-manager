from __future__ import annotations

from datetime import datetime

DATE_FORMATS = (
    "%Y:%m:%d %H:%M:%S",
    "%Y:%m:%d %H:%M:%S%z",
    "%Y:%m:%d %H:%M:%S.%f",
    "%Y:%m:%d %H:%M:%S.%f%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S%z",
    "%Y-%m-%d %H-%M-%S",
    "%Y-%m-%d %H-%M-%S%z",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y%m%d_%H%M%S",
    "%Y%m%d-%H%M%S",
    "%Y:%m:%d",
    "%Y-%m-%d",
    "%Y%m%d",
)

TRUNCATED_FORMATS = (
    "%Y:%m:%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H-%M-%S",
    "%Y-%m-%dT%H:%M:%S",
)


def _normalize_datetime_value(value: str) -> str:
    cleaned = value.strip()
    if cleaned.endswith("Z"):
        return cleaned[:-1] + "+00:00"
    return cleaned


def parse_datetime_value(value: str) -> datetime | None:
    raw = _normalize_datetime_value(value)

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    if len(raw) >= 19:
        truncated = raw[:19]
        for fmt in TRUNCATED_FORMATS:
            try:
                return datetime.strptime(truncated, fmt)
            except ValueError:
                continue

    return None


def format_resolution_value(value: datetime) -> str:
    if value.tzinfo is None:
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value.isoformat()


def describe_timezone_status(value: datetime) -> str:
    return "aware" if value.tzinfo is not None else "naive"
