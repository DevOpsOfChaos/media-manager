from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DIAGNOSTICS_PANEL_SCHEMA_VERSION = "1.0"


def _status_rank(status: str) -> int:
    return {"error": 0, "warning": 1, "ok": 2, "unknown": 3}.get(status, 4)


def build_diagnostic_item(item_id: str, title: str, *, status: str = "unknown", message: str = "", action_id: str | None = None) -> dict[str, object]:
    return {
        "id": item_id,
        "title": title,
        "status": status if status in {"ok", "warning", "error", "unknown"} else "unknown",
        "message": message,
        "action_id": action_id,
    }


def build_diagnostics_panel(*, backend_status: Mapping[str, Any] | None = None, bundle_validation: Mapping[str, Any] | None = None, model_health: Mapping[str, Any] | None = None) -> dict[str, object]:
    items: list[dict[str, object]] = []
    if backend_status is not None:
        available = bool(backend_status.get("available"))
        items.append(build_diagnostic_item("backend", "People backend", status="ok" if available else "warning", message=str(backend_status.get("next_action") or "")))
    if bundle_validation is not None:
        valid = bool(bundle_validation.get("valid", bundle_validation.get("status") == "ok"))
        problem_count = int(bundle_validation.get("problem_count", 0) or 0)
        items.append(build_diagnostic_item("people_bundle", "People review bundle", status="ok" if valid and problem_count == 0 else "error", message=f"{problem_count} problems"))
    if model_health is not None:
        valid = bool(model_health.get("valid", True))
        items.append(build_diagnostic_item("model_health", "GUI model health", status="ok" if valid else "warning", message=str(model_health.get("summary") or "")))
    items.sort(key=lambda item: (_status_rank(str(item.get("status"))), str(item.get("id"))))
    return {
        "schema_version": DIAGNOSTICS_PANEL_SCHEMA_VERSION,
        "kind": "diagnostics_panel",
        "item_count": len(items),
        "error_count": sum(1 for item in items if item.get("status") == "error"),
        "warning_count": sum(1 for item in items if item.get("status") == "warning"),
        "ok_count": sum(1 for item in items if item.get("status") == "ok"),
        "items": items,
    }


__all__ = ["DIAGNOSTICS_PANEL_SCHEMA_VERSION", "build_diagnostic_item", "build_diagnostics_panel"]
