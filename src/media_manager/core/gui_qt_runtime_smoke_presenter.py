from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_PRESENTER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def build_qt_runtime_smoke_presenter(workbench: Mapping[str, Any]) -> dict[str, object]:
    """Build a stable presenter model for the runtime smoke workbench."""

    summary = _mapping(workbench.get("summary"))
    sections = [section for section in _list(workbench.get("sections")) if isinstance(section, Mapping)]
    status = _text(workbench.get("status"), "pending")
    severity = {
        "ready": "success",
        "blocked": "error",
        "incomplete": "warning",
    }.get(status, "info")
    return {
        "schema_version": QT_RUNTIME_SMOKE_PRESENTER_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_presenter",
        "active_page_id": workbench.get("active_page_id"),
        "title": "Runtime Smoke",
        "subtitle": _text(workbench.get("message"), "Review Qt runtime readiness before opening a window."),
        "status": status,
        "severity": severity,
        "recommended_next_step": workbench.get("recommended_next_step"),
        "sections": [
            {
                "id": section.get("id"),
                "title": section.get("title"),
                "kind": section.get("kind"),
                "item_count": len(_list(section.get("items"))),
            }
            for section in sections
        ],
        "metrics": {
            "section_count": int(summary.get("section_count") or 0),
            "card_count": int(summary.get("card_count") or 0),
            "badge_count": int(summary.get("badge_count") or 0),
            "history_entry_count": int(summary.get("history_entry_count") or 0),
            "ready_for_runtime_review": bool(summary.get("ready_for_runtime_review")),
            "requires_user_confirmation": bool(summary.get("requires_user_confirmation", True)),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_smoke_presenter(presenter: Mapping[str, Any]) -> str:
    metrics = _mapping(presenter.get("metrics"))
    return "\n".join(
        [
            "Qt runtime smoke presenter",
            f"  Active page: {presenter.get('active_page_id')}",
            f"  Status: {presenter.get('status')}",
            f"  Severity: {presenter.get('severity')}",
            f"  Sections: {metrics.get('section_count', 0)}",
            f"  Ready: {metrics.get('ready_for_runtime_review')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_PRESENTER_SCHEMA_VERSION",
    "build_qt_runtime_smoke_presenter",
    "summarize_qt_runtime_smoke_presenter",
]
