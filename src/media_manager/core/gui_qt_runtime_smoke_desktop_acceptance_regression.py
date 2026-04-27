from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REGRESSION_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_regression(history_index: Mapping[str, Any], current_gate: Mapping[str, Any]) -> dict[str, object]:
    entries = history_index.get("entries") if isinstance(history_index.get("entries"), list) else []
    previous = entries[-1] if entries else {}
    previous_accepted = previous.get("accepted") if isinstance(previous, Mapping) else None
    current_accepted = bool(current_gate.get("ready"))
    regressed = previous_accepted is True and current_accepted is False
    improved = previous_accepted is False and current_accepted is True
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REGRESSION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_regression",
        "regressed": regressed,
        "improved": improved,
        "previous_accepted": previous_accepted,
        "current_accepted": current_accepted,
        "summary": {
            "regressed": regressed,
            "improved": improved,
            "has_history": bool(entries),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_REGRESSION_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_regression"]
