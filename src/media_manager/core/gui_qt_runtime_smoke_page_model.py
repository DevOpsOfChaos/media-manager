from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_detail_panel import build_qt_runtime_smoke_detail_panel
from .gui_qt_runtime_smoke_presenter import build_qt_runtime_smoke_presenter
from .gui_qt_runtime_smoke_table_model import build_qt_runtime_smoke_table_model

QT_RUNTIME_SMOKE_PAGE_MODEL_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_page_model(
    workbench: Mapping[str, Any],
    actions: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Compose a GUI-ready runtime smoke page model without importing Qt."""

    presenter = build_qt_runtime_smoke_presenter(workbench)
    table = build_qt_runtime_smoke_table_model(workbench)
    detail = build_qt_runtime_smoke_detail_panel(workbench)
    action_payload = _mapping(actions)
    metrics = _mapping(presenter.get("metrics"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_PAGE_MODEL_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_page_model",
        "page_id": "runtime-smoke",
        "title": presenter.get("title"),
        "subtitle": presenter.get("subtitle"),
        "active_page_id": workbench.get("active_page_id"),
        "presenter": presenter,
        "table": table,
        "detail": detail,
        "actions": list(action_payload.get("actions", [])) if isinstance(action_payload.get("actions"), list) else [],
        "layout": {
            "kind": "split_table_detail",
            "regions": ["header", "status", "table", "detail", "actions"],
            "opens_window": False,
        },
        "summary": {
            "row_count": _mapping(table.get("summary")).get("row_count", 0),
            "action_count": _mapping(action_payload.get("summary")).get("action_count", 0),
            "ready_for_runtime_review": metrics.get("ready_for_runtime_review", False),
            "ready_for_manual_smoke": metrics.get("ready_for_manual_smoke", False),
            "ready_to_start_manual_smoke": metrics.get("ready_to_start_manual_smoke", False),
            "evidence_complete": metrics.get("evidence_complete", False),
            "ready_for_release_gate": metrics.get("ready_for_release_gate", False),
            "requires_user_confirmation": metrics.get("requires_user_confirmation", True),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_PAGE_MODEL_SCHEMA_VERSION", "build_qt_runtime_smoke_page_model"]
