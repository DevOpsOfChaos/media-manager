from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_CARDS_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_result_cards(bundle: Mapping[str, Any]) -> dict[str, object]:
    summary = bundle.get("summary") if isinstance(bundle.get("summary"), Mapping) else {}
    cards = [
        {"id": "decision", "title": "Decision", "value": summary.get("decision"), "severity": "success" if bundle.get("accepted") else "error"},
        {"id": "results", "title": "Results", "value": summary.get("result_count", 0), "severity": "info"},
        {"id": "failed", "title": "Failed required", "value": summary.get("failed_required_count", 0), "severity": "error" if summary.get("failed_required_count") else "success"},
        {"id": "missing", "title": "Missing required", "value": summary.get("missing_required_count", 0), "severity": "warning" if summary.get("missing_required_count") else "success"},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_CARDS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_cards",
        "cards": cards,
        "summary": {
            "card_count": len(cards),
            "accepted": bool(bundle.get("accepted")),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_CARDS_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_result_cards"]
