from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ROLLOUT_PLAN_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_rollout_plan(gate: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, object]:
    allowed = bool(gate.get("ready")) and quality.get("summary", {}).get("ready") is True if isinstance(quality.get("summary"), Mapping) else bool(gate.get("ready"))
    phases = [
        {"id": "keep-headless-contract-tests", "enabled": True},
        {"id": "wire-runtime-smoke-page-behind-guard", "enabled": allowed},
        {"id": "manual-qt-window-smoke", "enabled": allowed},
        {"id": "capture-metadata-only-result", "enabled": allowed},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ROLLOUT_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_rollout_plan",
        "allowed": allowed,
        "phases": [{**phase, "executes_immediately": False, "manual_only": True} for phase in phases],
        "summary": {
            "phase_count": len(phases),
            "enabled_phase_count": sum(1 for phase in phases if phase["enabled"]),
            "manual_only": True,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_ROLLOUT_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_rollout_plan"]
