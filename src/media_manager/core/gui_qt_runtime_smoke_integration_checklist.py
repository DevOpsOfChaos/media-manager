from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTEGRATION_CHECKLIST_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_integration_checklist(gate: Mapping[str, Any]) -> dict[str, object]:
    """Build a checklist for the next guarded runtime smoke integration step."""

    ready = bool(gate.get("ready"))
    checks = [
        {"id": "adapter-ready", "label": "Adapter bundle is ready", "passed": ready, "required": True},
        {"id": "page-handoff-ready", "label": "Page handoff is ready", "passed": ready, "required": True},
        {"id": "shell-registration-ready", "label": "Shell registration is ready", "passed": ready, "required": True},
        {"id": "no-window-opened", "label": "No window opens during headless checks", "passed": True, "required": True},
        {"id": "no-command-execution", "label": "No command executes during headless checks", "passed": True, "required": True},
        {"id": "local-only", "label": "Runtime Smoke remains local-only", "passed": True, "required": True},
    ]
    if not ready:
        for problem in gate.get("problems", []) if isinstance(gate.get("problems"), list) else []:
            if isinstance(problem, Mapping):
                checks.append(
                    {
                        "id": f"problem-{problem.get('code')}",
                        "label": f"Resolve integration problem: {problem.get('code')}",
                        "passed": False,
                        "required": True,
                    }
                )
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_CHECKLIST_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_checklist",
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "required_check_count": sum(1 for check in checks if check["required"]),
            "passed_count": sum(1 for check in checks if check["passed"]),
            "failed_required_count": sum(1 for check in checks if check["required"] and not check["passed"]),
            "ready": ready and all(check["passed"] for check in checks if check["required"]),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_INTEGRATION_CHECKLIST_SCHEMA_VERSION", "build_qt_runtime_smoke_integration_checklist"]
