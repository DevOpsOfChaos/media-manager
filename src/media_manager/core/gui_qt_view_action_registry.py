from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ACTION_REGISTRY_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, fallback: str = "") -> str:
    return str(value).strip() if value is not None and str(value).strip() else fallback


def _bool(value: Any, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def normalize_view_action(action: Mapping[str, Any], *, source: str = "page") -> dict[str, object]:
    """Normalize GUI actions into a stable registry row.

    The registry is intentionally non-executing. Actions describe UI intent and safety
    requirements; execution is handled by later guarded layers.
    """
    action_id = _text(action.get("id") or action.get("action_id"), "action")
    risk = _text(action.get("risk_level"), "safe")
    requires_confirmation = _bool(action.get("requires_confirmation"), risk in {"high", "danger", "destructive"})
    enabled = _bool(action.get("enabled"), True)
    return {
        "schema_version": ACTION_REGISTRY_SCHEMA_VERSION,
        "id": action_id,
        "label": _text(action.get("label"), action_id.replace("_", " ").title()),
        "category": _text(action.get("category"), source),
        "source": source,
        "enabled": enabled,
        "recommended": _bool(action.get("recommended")),
        "risk_level": risk,
        "requires_confirmation": requires_confirmation,
        "shortcut": action.get("shortcut"),
        "page_id": action.get("page_id"),
        "intent": action.get("intent") if isinstance(action.get("intent"), Mapping) else None,
        "executes_immediately": False,
    }


def build_view_action_registry(
    *,
    page_model: Mapping[str, Any] | None = None,
    page_actions: Iterable[Mapping[str, Any]] | None = None,
    navigation: Iterable[Mapping[str, Any]] | None = None,
    command_palette: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    page_model = _as_mapping(page_model)
    rows: list[dict[str, object]] = []

    for raw in list(page_actions or ()) + [item for item in _as_list(page_model.get("quick_actions")) if isinstance(item, Mapping)]:
        rows.append(normalize_view_action(raw, source="page"))

    for raw in navigation or ():
        nav = _as_mapping(raw)
        if not nav:
            continue
        rows.append(
            normalize_view_action(
                {
                    "id": f"navigate_{_text(nav.get('id'), 'page')}",
                    "label": nav.get("label"),
                    "category": "navigation",
                    "enabled": nav.get("enabled", True),
                    "shortcut": nav.get("shortcut"),
                    "page_id": nav.get("id"),
                    "intent": {"type": "navigate", "page_id": nav.get("id")},
                },
                source="navigation",
            )
        )

    palette = _as_mapping(command_palette)
    for raw in _as_list(palette.get("items")):
        item = _as_mapping(raw)
        if item:
            rows.append(normalize_view_action(item, source="command_palette"))

    seen: set[str] = set()
    unique_rows: list[dict[str, object]] = []
    for row in rows:
        action_id = str(row["id"])
        if action_id in seen:
            continue
        seen.add(action_id)
        unique_rows.append(row)

    return {
        "schema_version": ACTION_REGISTRY_SCHEMA_VERSION,
        "kind": "qt_view_action_registry",
        "actions": unique_rows,
        "action_count": len(unique_rows),
        "enabled_count": sum(1 for row in unique_rows if row.get("enabled")),
        "confirmation_count": sum(1 for row in unique_rows if row.get("requires_confirmation")),
        "danger_count": sum(1 for row in unique_rows if row.get("risk_level") in {"high", "danger", "destructive"}),
        "executes_immediately": False,
    }


__all__ = [
    "ACTION_REGISTRY_SCHEMA_VERSION",
    "build_view_action_registry",
    "normalize_view_action",
]
