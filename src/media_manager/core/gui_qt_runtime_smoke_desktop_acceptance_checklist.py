from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_CHECKLIST_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_checklist(gate: Mapping[str, Any], redaction: Mapping[str, Any]) -> dict[str, object]:
    redaction_summary = redaction.get("summary") if isinstance(redaction.get("summary"), Mapping) else {}
    checks = [
        {"id": "gate-ready", "passed": bool(gate.get("ready")), "required": True},
        {"id": "metadata-only", "passed": redaction_summary.get("metadata_only") is True, "required": True},
        {"id": "no-sensitive-media", "passed": int(redaction_summary.get("sensitive_media_count") or 0) == 0, "required": True},
        {"id": "no-window-open", "passed": True, "required": True},
        {"id": "no-command-execution", "passed": True, "required": True},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_CHECKLIST_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_checklist",
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "failed_required_count": sum(1 for check in checks if check["required"] and not check["passed"]),
            "ready": all(check["passed"] for check in checks if check["required"]),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_CHECKLIST_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_checklist"]
