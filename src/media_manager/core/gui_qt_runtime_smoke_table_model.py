from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_TABLE_MODEL_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _row_from_card(card: Mapping[str, Any], index: int) -> dict[str, object]:
    details = _mapping(card.get("details"))
    return {
        "row_id": str(card.get("id") or f"card-{index + 1}"),
        "title": str(card.get("title") or "Metric"),
        "metric": card.get("metric"),
        "problem_count": int(details.get("problem_count") or 0),
        "privacy_check_count": int(details.get("privacy_check_count") or 0),
        "artifact_count": int(details.get("artifact_count") or 0),
        "ready": card.get("metric") == "ready" or details.get("ready_for_runtime_review") is True,
    }


def build_qt_runtime_smoke_table_model(workbench: Mapping[str, Any]) -> dict[str, object]:
    """Build a table-friendly model from runtime smoke workbench cards."""

    cards_section = next(
        (
            section
            for section in _list(workbench.get("sections"))
            if isinstance(section, Mapping) and section.get("kind") == "metric_cards"
        ),
        {},
    )
    rows = [
        _row_from_card(card, index)
        for index, card in enumerate(_list(_mapping(cards_section).get("items")))
        if isinstance(card, Mapping)
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_TABLE_MODEL_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_table_model",
        "active_page_id": workbench.get("active_page_id"),
        "columns": ["title", "metric", "problem_count", "privacy_check_count", "artifact_count", "ready"],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "ready_row_count": sum(1 for row in rows if row.get("ready")),
            "problem_count_total": sum(int(row.get("problem_count") or 0) for row in rows),
            "privacy_check_count_total": sum(int(row.get("privacy_check_count") or 0) for row in rows),
            "artifact_count_total": sum(int(row.get("artifact_count") or 0) for row in rows),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_TABLE_MODEL_SCHEMA_VERSION", "build_qt_runtime_smoke_table_model"]
