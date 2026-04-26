from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

FILTER_PRESET_SCHEMA_VERSION = "1.0"


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def build_filter_preset(preset_id: str, label: str, *, status: str | None = None, query: str = "", risk: str | None = None) -> dict[str, object]:
    return {
        "schema_version": FILTER_PRESET_SCHEMA_VERSION,
        "kind": "gui_filter_preset",
        "id": _as_text(preset_id) or "all",
        "label": _as_text(label) or _as_text(preset_id) or "All",
        "query": _as_text(query),
        "status": status or None,
        "risk": risk or None,
    }


def default_people_review_filter_presets(*, language: str = "en") -> list[dict[str, object]]:
    de = str(language).lower().startswith("de")
    return [
        build_filter_preset("all", "Alle" if de else "All"),
        build_filter_preset("needs-name", "Name fehlt" if de else "Needs name", status="needs_name"),
        build_filter_preset("needs-review", "Zu prüfen" if de else "Needs review", status="needs_review"),
        build_filter_preset("ready", "Bereit" if de else "Ready", status="ready_to_apply"),
        build_filter_preset("rejected", "Abgelehnt" if de else "Rejected", status="all_faces_rejected"),
    ]


def default_run_filter_presets(*, language: str = "en") -> list[dict[str, object]]:
    de = str(language).lower().startswith("de")
    return [
        build_filter_preset("all", "Alle" if de else "All"),
        build_filter_preset("errors", "Fehler" if de else "Errors", risk="error"),
        build_filter_preset("needs-review", "Zu prüfen" if de else "Needs review", status="needs_review"),
        build_filter_preset("people", "Personen" if de else "People", query="people"),
    ]


def apply_filter_preset(items: Iterable[Mapping[str, Any]], preset: Mapping[str, Any]) -> list[dict[str, object]]:
    status = preset.get("status")
    risk = preset.get("risk")
    query = _as_text(preset.get("query")).casefold()
    result: list[dict[str, object]] = []
    for item in items:
        item_status = item.get("status")
        haystack = " ".join(str(value) for value in item.values() if value is not None).casefold()
        if status and item_status != status:
            continue
        if risk == "error" and item.get("exit_code") in (None, 0) and item_status not in {"error", "failed", "blocked"}:
            continue
        if query and query not in haystack:
            continue
        result.append(dict(item))
    return result


def mark_active_preset(presets: Iterable[Mapping[str, Any]], active_preset_id: str) -> list[dict[str, object]]:
    active = _as_text(active_preset_id) or "all"
    return [{**dict(item), "active": item.get("id") == active} for item in presets]


__all__ = [
    "FILTER_PRESET_SCHEMA_VERSION",
    "apply_filter_preset",
    "build_filter_preset",
    "default_people_review_filter_presets",
    "default_run_filter_presets",
    "mark_active_preset",
]
