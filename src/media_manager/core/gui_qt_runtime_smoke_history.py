from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

QT_RUNTIME_SMOKE_HISTORY_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_smoke_history_entry(
    smoke_report: Mapping[str, Any],
    *,
    report_path: str = "",
    commit_sha: str = "",
    recorded_at_utc: str | None = None,
) -> dict[str, object]:
    summary = _mapping(smoke_report.get("summary"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_HISTORY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_history_entry",
        "recorded_at_utc": recorded_at_utc or _now_utc(),
        "active_page_id": smoke_report.get("active_page_id"),
        "report_path": _text(report_path),
        "commit_sha": _text(commit_sha),
        "ready_for_release_gate": bool(smoke_report.get("ready_for_release_gate")),
        "check_count": int(summary.get("check_count") or 0),
        "result_count": int(summary.get("result_count") or 0),
        "problem_count": int(summary.get("problem_count") or 0),
        "privacy_check_count": int(summary.get("privacy_check_count") or 0),
        "local_only": True,
    }


def build_qt_runtime_smoke_history(entries: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    normalized = [dict(item) for item in (entries or []) if isinstance(item, Mapping)]
    return {
        "schema_version": QT_RUNTIME_SMOKE_HISTORY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_history",
        "entries": normalized,
        "summary": summarize_qt_runtime_smoke_history(normalized),
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def append_qt_runtime_smoke_history_entry(
    history: Mapping[str, Any] | list[Mapping[str, Any]],
    smoke_report: Mapping[str, Any],
    *,
    report_path: str = "",
    commit_sha: str = "",
    recorded_at_utc: str | None = None,
) -> dict[str, object]:
    entries = _list(history.get("entries")) if isinstance(history, Mapping) else list(history)
    entry = build_qt_runtime_smoke_history_entry(
        smoke_report,
        report_path=report_path,
        commit_sha=commit_sha,
        recorded_at_utc=recorded_at_utc,
    )
    return build_qt_runtime_smoke_history([*(item for item in entries if isinstance(item, Mapping)), entry])


def summarize_qt_runtime_smoke_history(history_or_entries: Mapping[str, Any] | list[Mapping[str, Any]]) -> dict[str, object]:
    entries = _list(history_or_entries.get("entries")) if isinstance(history_or_entries, Mapping) else list(history_or_entries)
    valid_entries = [entry for entry in entries if isinstance(entry, Mapping)]
    ready_entries = [entry for entry in valid_entries if entry.get("ready_for_release_gate") is True]
    failed_entries = [entry for entry in valid_entries if entry.get("ready_for_release_gate") is False]
    latest = valid_entries[-1] if valid_entries else {}
    return {
        "schema_version": QT_RUNTIME_SMOKE_HISTORY_SCHEMA_VERSION,
        "entry_count": len(valid_entries),
        "ready_count": len(ready_entries),
        "not_ready_count": len(failed_entries),
        "problem_count_total": sum(int(_mapping(entry).get("problem_count") or 0) for entry in valid_entries),
        "privacy_check_count_total": sum(int(_mapping(entry).get("privacy_check_count") or 0) for entry in valid_entries),
        "latest_active_page_id": latest.get("active_page_id"),
        "latest_ready_for_release_gate": latest.get("ready_for_release_gate"),
    }


__all__ = [
    "QT_RUNTIME_SMOKE_HISTORY_SCHEMA_VERSION",
    "append_qt_runtime_smoke_history_entry",
    "build_qt_runtime_smoke_history",
    "build_qt_runtime_smoke_history_entry",
    "summarize_qt_runtime_smoke_history",
]
