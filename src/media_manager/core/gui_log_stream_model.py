from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

LOG_STREAM_SCHEMA_VERSION = "1.0"
LOG_LEVELS = ("debug", "info", "warning", "error")


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_log_level(level: object) -> str:
    value = str(level or "info").strip().lower()
    return value if value in LOG_LEVELS else "info"


def build_log_entry(message: object, *, level: str = "info", source: str = "gui", job_id: str | None = None) -> dict[str, object]:
    return {
        "schema_version": LOG_STREAM_SCHEMA_VERSION,
        "timestamp_utc": _now_utc(),
        "level": normalize_log_level(level),
        "source": source,
        "job_id": job_id,
        "message": str(message),
    }


def build_log_stream(entries: Sequence[Mapping[str, Any]] = (), *, limit: int | None = None) -> dict[str, object]:
    values = [dict(item) for item in entries]
    if limit is not None and limit >= 0:
        values = values[-limit:]
    summary: dict[str, int] = {}
    for item in values:
        level = normalize_log_level(item.get("level"))
        summary[level] = summary.get(level, 0) + 1
    return {
        "schema_version": LOG_STREAM_SCHEMA_VERSION,
        "kind": "gui_log_stream",
        "entries": values,
        "entry_count": len(values),
        "level_summary": dict(sorted(summary.items())),
        "has_errors": summary.get("error", 0) > 0,
    }


def append_log_entry(stream: Mapping[str, Any], message: object, *, level: str = "info", source: str = "gui", job_id: str | None = None) -> dict[str, object]:
    entries = [dict(item) for item in stream.get("entries", []) if isinstance(item, Mapping)]
    entries.append(build_log_entry(message, level=level, source=source, job_id=job_id))
    return build_log_stream(entries)


__all__ = ["LOG_LEVELS", "LOG_STREAM_SCHEMA_VERSION", "append_log_entry", "build_log_entry", "build_log_stream", "normalize_log_level"]
