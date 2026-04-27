from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_VISIBLE_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _section(section_id: str, title: str, component: str, *, props: Mapping[str, Any] | None = None, items: list[Any] | None = None) -> dict[str, object]:
    return {
        "id": section_id,
        "title": title,
        "component": component,
        "props": dict(props or {}),
        "items": list(items or []),
        "item_count": len(list(items or [])),
    }


def build_qt_runtime_smoke_visible_plan(page_model: Mapping[str, Any]) -> dict[str, object]:
    """Convert the runtime smoke page model into a visible, headless Qt plan."""

    presenter = _mapping(page_model.get("presenter"))
    table = _mapping(page_model.get("table"))
    detail = _mapping(page_model.get("detail"))
    actions = [dict(action) for action in _list(page_model.get("actions")) if isinstance(action, Mapping)]
    presenter_metrics = _mapping(presenter.get("metrics"))
    table_summary = _mapping(table.get("summary"))
    detail_privacy = _mapping(detail.get("privacy"))

    status_section = _section(
        "runtime-smoke-status",
        "Runtime smoke status",
        "StatusBanner",
        props={
            "status": presenter.get("status"),
            "severity": presenter.get("severity"),
            "message": presenter.get("subtitle"),
            "ready": bool(presenter_metrics.get("ready_for_runtime_review")),
        },
    )
    table_section = _section(
        "runtime-smoke-table",
        "Runtime smoke metrics",
        "DataTable",
        props={
            "columns": list(_list(table.get("columns"))),
            "row_count": table_summary.get("row_count", 0),
            "problem_count_total": table_summary.get("problem_count_total", 0),
        },
        items=[dict(row) for row in _list(table.get("rows")) if isinstance(row, Mapping)],
    )
    detail_section = _section(
        "runtime-smoke-detail",
        "Runtime smoke detail",
        "DetailPanel",
        props={
            "status": detail.get("status"),
            "recommended_next_step": detail.get("recommended_next_step"),
            "local_only": bool(detail_privacy.get("local_only", True)),
            "network_required": bool(detail_privacy.get("network_required", False)),
        },
    )
    action_section = _section(
        "runtime-smoke-actions",
        "Runtime smoke actions",
        "ActionBar",
        props={
            "action_count": len(actions),
            "confirmation_action_count": sum(1 for action in actions if action.get("requires_confirmation")),
            "executes_immediately": False,
        },
        items=actions,
    )
    sections = [status_section, table_section, detail_section, action_section]
    return {
        "schema_version": QT_RUNTIME_SMOKE_VISIBLE_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_visible_plan",
        "page_id": page_model.get("page_id") or "runtime-smoke",
        "title": page_model.get("title") or presenter.get("title") or "Runtime Smoke",
        "subtitle": page_model.get("subtitle") or presenter.get("subtitle"),
        "active_page_id": page_model.get("active_page_id"),
        "sections": sections,
        "summary": {
            "section_count": len(sections),
            "row_count": table_summary.get("row_count", 0),
            "action_count": len(actions),
            "ready_for_runtime_review": bool(presenter_metrics.get("ready_for_runtime_review")),
            "contains_sensitive_people_data_possible": bool(detail_privacy.get("contains_sensitive_people_data_possible")),
            "local_only": bool(detail_privacy.get("local_only", True)),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_VISIBLE_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_visible_plan"]
