from __future__ import annotations

import importlib.util
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_QT_BACKEND_PROBE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_qt_backend_probe() -> dict[str, object]:
    """Probe optional Qt availability without importing PySide6 or opening a window."""

    available = importlib.util.find_spec("PySide6") is not None
    return {
        "schema_version": QT_RUNTIME_SMOKE_QT_BACKEND_PROBE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_qt_backend_probe",
        "binding": "PySide6",
        "available": available,
        "probe_method": "importlib.util.find_spec",
        "imports_backend": False,
        "opens_window": False,
        "install_hint": 'python -m pip install -e ".[gui]"',
        "summary": {
            "available": available,
            "requires_install": not available,
            "safe_to_run_headless": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_smoke_qt_backend_probe(probe: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "Qt backend probe",
            f"  Binding: {probe.get('binding')}",
            f"  Available: {probe.get('available')}",
            f"  Imports backend: {probe.get('imports_backend')}",
            f"  Opens window: {probe.get('opens_window')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_QT_BACKEND_PROBE_SCHEMA_VERSION",
    "build_qt_runtime_smoke_qt_backend_probe",
    "summarize_qt_runtime_smoke_qt_backend_probe",
]
