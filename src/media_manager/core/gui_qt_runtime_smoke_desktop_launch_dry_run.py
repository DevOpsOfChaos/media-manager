from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_DRY_RUN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_launch_dry_run(
    *,
    wiring_bundle: Mapping[str, Any],
    rehearsal_bundle: Mapping[str, Any],
    start_bundle: Mapping[str, Any],
    backend_probe: Mapping[str, Any],
) -> dict[str, object]:
    """Build a non-executing dry-run for the future manual Qt smoke launch."""

    checks = [
        {
            "id": "guarded-wiring-ready",
            "label": "Guarded shell wiring is ready",
            "passed": bool(wiring_bundle.get("ready_for_guarded_shell_wiring")),
            "required": True,
        },
        {
            "id": "desktop-rehearsal-ready",
            "label": "Desktop rehearsal is ready",
            "passed": bool(rehearsal_bundle.get("ready_for_manual_desktop_smoke")),
            "required": True,
        },
        {
            "id": "desktop-start-bundle-ready",
            "label": "Manual desktop start bundle is ready",
            "passed": bool(start_bundle.get("ready_for_manual_desktop_start")),
            "required": True,
        },
        {
            "id": "qt-backend-present",
            "label": "PySide6 can be installed before manual run",
            "passed": True,
            "required": False,
            "current_available": bool(backend_probe.get("available")),
        },
    ]
    failed_required = [check for check in checks if check.get("required") and check.get("passed") is not True]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_DRY_RUN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_launch_dry_run",
        "checks": checks,
        "ready": not failed_required,
        "execution_policy": {
            "mode": "dry_run_only",
            "opens_window": False,
            "executes_commands": False,
            "requires_user_confirmation": True,
        },
        "summary": {
            "check_count": len(checks),
            "failed_required_count": len(failed_required),
            "ready": not failed_required,
            "qt_backend_available": bool(backend_probe.get("available")),
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


__all__ = [
    "QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_DRY_RUN_SCHEMA_VERSION",
    "build_qt_runtime_smoke_desktop_launch_dry_run",
]
