from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_WORKBENCH_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _status_from_dashboard(dashboard: Mapping[str, Any]) -> tuple[str, str]:
    summary = _mapping(dashboard.get("summary"))
    if dashboard.get("ready_for_runtime_review") is True:
        return "ready", "Ready for manual runtime review"
    if _int(summary.get("blocked_badge_count")) > 0:
        return "blocked", "Resolve failed runtime smoke checks"
    if _int(summary.get("incomplete_badge_count")) > 0:
        return "incomplete", "Complete missing runtime smoke results"
    return "pending", "Record runtime smoke evidence"


def build_qt_runtime_smoke_workbench(
    dashboard: Mapping[str, Any],
    decision: Mapping[str, Any] | None = None,
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build a GUI-ready, headless workbench model for runtime smoke review."""

    status, message = _status_from_dashboard(dashboard)
    summary = _mapping(dashboard.get("summary"))
    status_strip = _mapping(dashboard.get("status_strip"))
    trend = _mapping(dashboard.get("trend"))
    cards = [dict(card) for card in _list(dashboard.get("cards")) if isinstance(card, Mapping)]
    dec = dict(decision or {})
    action = dec.get("recommended_next_step") or message

    sections = [
        {"id": "runtime-smoke-status", "title": "Runtime smoke status", "kind": "status_strip", "items": list(_list(status_strip.get("badges")))},
        {"id": "runtime-smoke-cards", "title": "Runtime smoke metrics", "kind": "metric_cards", "items": cards},
        {"id": "runtime-smoke-trend", "title": "Runtime smoke trend", "kind": "trend", "items": list(_list(trend.get("points"))), "summary": dict(_mapping(trend.get("summary")))},
    ]

    ready_to_start = bool(summary.get("ready_to_start_manual_smoke") or summary.get("ready_for_manual_smoke"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_WORKBENCH_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_workbench",
        "language": "de" if language == "de" else "en",
        "active_page_id": dashboard.get("active_page_id"),
        "status": status,
        "message": message,
        "decision": dec,
        "recommended_next_step": action,
        "sections": sections,
        "summary": {
            "section_count": len(sections),
            "card_count": len(cards),
            "badge_count": _int(_mapping(status_strip.get("summary")).get("badge_count")),
            "history_entry_count": _int(summary.get("history_entry_count")),
            "ready_for_runtime_review": bool(dashboard.get("ready_for_runtime_review")),
            "ready_for_manual_smoke": ready_to_start,
            "ready_to_start_manual_smoke": ready_to_start,
            "evidence_complete": bool(summary.get("evidence_complete")),
            "ready_for_release_gate": bool(summary.get("ready_for_release_gate")),
            "requires_user_confirmation": bool(dec.get("requires_user_confirmation", True)),
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


def summarize_qt_runtime_smoke_workbench(workbench: Mapping[str, Any]) -> str:
    summary = _mapping(workbench.get("summary"))
    return "\n".join(["Qt runtime smoke workbench", f"  Active page: {workbench.get('active_page_id')}", f"  Status: {workbench.get('status')}", f"  Sections: {summary.get('section_count', 0)}", f"  Cards: {summary.get('card_count', 0)}", f"  Ready: {summary.get('ready_for_runtime_review')}"])


__all__ = ["QT_RUNTIME_SMOKE_WORKBENCH_SCHEMA_VERSION", "build_qt_runtime_smoke_workbench", "summarize_qt_runtime_smoke_workbench"]
