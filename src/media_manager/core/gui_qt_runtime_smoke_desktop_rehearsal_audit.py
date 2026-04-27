from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_AUDIT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def audit_qt_runtime_smoke_desktop_rehearsal(
    rehearsal_plan: Mapping[str, Any],
    preflight: Mapping[str, Any],
    session_plan: Mapping[str, Any],
    launch_notes: Mapping[str, Any],
) -> dict[str, object]:
    """Audit the full headless desktop rehearsal contract."""

    problems: list[dict[str, object]] = []
    if rehearsal_plan.get("ready") is not True:
        problems.append({"code": "rehearsal_plan_not_ready"})
    if _mapping(preflight.get("summary")).get("ready") is not True:
        problems.append({"code": "preflight_not_ready"})
    if session_plan.get("ready") is not True:
        problems.append({"code": "session_plan_not_ready"})
    if launch_notes.get("ready") is not True:
        problems.append({"code": "launch_notes_not_ready"})
    for name, payload in [("rehearsal_plan", rehearsal_plan), ("preflight", preflight), ("session_plan", session_plan), ("launch_notes", launch_notes)]:
        caps = _mapping(payload.get("capabilities"))
        if caps.get("opens_window") is not False:
            problems.append({"code": "opens_window", "source": name})
        if caps.get("executes_commands") is not False:
            problems.append({"code": "executes_commands", "source": name})
        if caps.get("local_only") is not True:
            problems.append({"code": "not_local_only", "source": name})
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_AUDIT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_rehearsal_audit",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "valid": not problems,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_AUDIT_SCHEMA_VERSION", "audit_qt_runtime_smoke_desktop_rehearsal"]
