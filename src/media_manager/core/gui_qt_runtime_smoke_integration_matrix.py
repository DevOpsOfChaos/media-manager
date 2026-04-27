from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTEGRATION_MATRIX_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool_cap(payload: Mapping[str, Any], name: str, default: bool = False) -> bool:
    caps = _mapping(payload.get("capabilities"))
    return bool(caps.get(name, default))


def _status(name: str, payload: Mapping[str, Any], *, ready_key: str = "ready") -> dict[str, object]:
    summary = _mapping(payload.get("summary"))
    ready = bool(payload.get(ready_key) or summary.get(ready_key))
    return {
        "id": name,
        "kind": payload.get("kind"),
        "ready": ready,
        "problem_count": int(payload.get("problem_count") or summary.get("problem_count") or 0),
        "requires_pyside6": _bool_cap(payload, "requires_pyside6"),
        "opens_window": _bool_cap(payload, "opens_window"),
        "executes_commands": _bool_cap(payload, "executes_commands"),
        "local_only": _bool_cap(payload, "local_only", True),
    }


def build_qt_runtime_smoke_integration_matrix(
    *,
    adapter_bundle: Mapping[str, Any],
    page_handoff: Mapping[str, Any],
    shell_bundle: Mapping[str, Any],
) -> dict[str, object]:
    """Build a matrix covering the Runtime Smoke integration chain."""

    rows = [
        _status("adapter", adapter_bundle, ready_key="ready_for_qt_runtime"),
        _status("page_handoff", page_handoff, ready_key="ready_for_shell_registration"),
        _status("shell", shell_bundle, ready_key="ready_for_shell"),
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_MATRIX_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_matrix",
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "ready_count": sum(1 for row in rows if row["ready"]),
            "problem_count_total": sum(int(row["problem_count"]) for row in rows),
            "requires_pyside6_count": sum(1 for row in rows if row["requires_pyside6"]),
            "opens_window_count": sum(1 for row in rows if row["opens_window"]),
            "executes_commands_count": sum(1 for row in rows if row["executes_commands"]),
            "local_only_count": sum(1 for row in rows if row["local_only"]),
            "all_ready": all(row["ready"] for row in rows),
            "all_local_only": all(row["local_only"] for row in rows),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_INTEGRATION_MATRIX_SCHEMA_VERSION", "build_qt_runtime_smoke_integration_matrix"]
