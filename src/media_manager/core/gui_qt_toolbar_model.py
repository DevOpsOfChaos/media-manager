from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

TOOLBAR_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def _bucket(action: Mapping[str, Any]) -> str:
    if not action.get("enabled", True):
        return "disabled"
    if action.get("requires_confirmation") or action.get("risk_level") in {"high", "destructive", "danger"}:
        return "danger"
    if action.get("recommended") or action.get("variant") == "primary":
        return "primary"
    return "secondary"


def build_qt_toolbar_model(actions: Sequence[Mapping[str, Any]], *, title: str = "") -> dict[str, object]:
    buttons: list[dict[str, object]] = []
    bucket_summary = {"primary": 0, "secondary": 0, "danger": 0, "disabled": 0}
    for action in actions:
        bucket = _bucket(action)
        bucket_summary[bucket] += 1
        buttons.append(
            {
                "id": _text(action.get("id")),
                "label": _text(action.get("label") or action.get("id")),
                "enabled": bool(action.get("enabled", True)),
                "bucket": bucket,
                "requires_confirmation": bool(action.get("requires_confirmation")),
                "object_name": f"ToolbarButton{bucket.title()}",
            }
        )
    return {
        "schema_version": TOOLBAR_SCHEMA_VERSION,
        "kind": "qt_toolbar_model",
        "title": title,
        "button_count": len(buttons),
        "bucket_summary": bucket_summary,
        "buttons": buttons,
    }


__all__ = ["TOOLBAR_SCHEMA_VERSION", "build_qt_toolbar_model"]
