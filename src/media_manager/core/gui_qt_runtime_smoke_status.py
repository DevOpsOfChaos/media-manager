from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_STATUS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_smoke_status_badge(source: Mapping[str, Any], *, label: str = "Runtime smoke") -> dict[str, object]:
    summary = _mapping(source.get("summary"))
    ready = bool(source.get("ready_for_release_gate") or summary.get("ready_for_release_gate"))
    problem_count = _int(summary.get("problem_count") or source.get("problem_count"))
    missing_count = _int(summary.get("missing_required_count") or summary.get("missing_smoke_check_count"))
    failed_count = _int(summary.get("failed_required_count"))
    if ready and problem_count == 0 and missing_count == 0 and failed_count == 0:
        state, severity, text = "ready", "success", "Ready"
    elif problem_count > 0 or failed_count > 0:
        state, severity, text = "blocked", "error", "Blocked"
    elif missing_count > 0:
        state, severity, text = "incomplete", "warning", "Incomplete"
    else:
        state, severity, text = "pending", "info", "Pending"
    return {
        "schema_version": QT_RUNTIME_SMOKE_STATUS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_status_badge",
        "label": label,
        "state": state,
        "severity": severity,
        "text": text,
        "problem_count": problem_count,
        "missing_required_count": missing_count,
        "failed_required_count": failed_count,
        "ready": state == "ready",
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


def build_qt_runtime_smoke_status_strip(items: list[Mapping[str, Any]]) -> dict[str, object]:
    badges = [build_qt_runtime_smoke_status_badge(item, label=str(item.get("label") or item.get("kind") or f"Item {index + 1}")) for index, item in enumerate(items) if isinstance(item, Mapping)]
    return {
        "schema_version": QT_RUNTIME_SMOKE_STATUS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_status_strip",
        "badges": badges,
        "summary": {
            "badge_count": len(badges),
            "ready_count": sum(1 for badge in badges if badge["state"] == "ready"),
            "blocked_count": sum(1 for badge in badges if badge["state"] == "blocked"),
            "incomplete_count": sum(1 for badge in badges if badge["state"] == "incomplete"),
            "pending_count": sum(1 for badge in badges if badge["state"] == "pending"),
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


__all__ = ["QT_RUNTIME_SMOKE_STATUS_SCHEMA_VERSION", "build_qt_runtime_smoke_status_badge", "build_qt_runtime_smoke_status_strip"]
