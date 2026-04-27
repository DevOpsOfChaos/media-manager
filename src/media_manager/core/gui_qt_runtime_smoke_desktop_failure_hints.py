from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_FAILURE_HINTS_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_failure_hints(preflight: Mapping[str, Any]) -> dict[str, object]:
    """Create troubleshooting hints from failed preflight checks."""

    failed = [check for check in _list(preflight.get("checks")) if isinstance(check, Mapping) and check.get("required") and not check.get("passed")]
    hints = []
    hint_map = {
        "plan-ready": "Rebuild the Runtime Smoke wiring bundle before manual launch.",
        "wiring-clean": "Inspect wiring audit, integration gate, and shell readiness reports.",
        "manual-only-launch": "Do not proceed until launch policy is manual-only.",
        "no-headless-window": "Headless preflight must not open a window.",
        "no-command-execution": "Headless preflight must not execute commands.",
        "local-only": "Fix local-only privacy flags before continuing.",
    }
    for item in failed:
        check_id = str(item.get("id"))
        hints.append({"check_id": check_id, "hint": hint_map.get(check_id, "Review the failed preflight check."), "blocking": True})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_FAILURE_HINTS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_failure_hints",
        "hints": hints,
        "summary": {
            "hint_count": len(hints),
            "blocking_hint_count": sum(1 for hint in hints if hint["blocking"]),
            "has_blockers": bool(hints),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_FAILURE_HINTS_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_failure_hints"]
