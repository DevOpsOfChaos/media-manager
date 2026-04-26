from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

INTERACTION_BINDINGS_SCHEMA_VERSION = "1.0"


def build_interaction_binding(
    action_id: str,
    *,
    event: str = "click",
    target: str | None = None,
    page_id: str | None = None,
    requires_confirmation: bool = False,
    enabled: bool = True,
) -> dict[str, object]:
    return {
        "schema_version": INTERACTION_BINDINGS_SCHEMA_VERSION,
        "action_id": action_id,
        "event": event,
        "target": target or action_id,
        "page_id": page_id,
        "enabled": bool(enabled),
        "requires_confirmation": bool(requires_confirmation),
        "executes_immediately": False,
    }


def build_page_interaction_bindings(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "")
    raw_actions: list[Any] = []
    for key in ("actions", "quick_actions", "page_actions"):
        value = page_model.get(key)
        if isinstance(value, list):
            raw_actions.extend(value)
    bindings = []
    for item in raw_actions:
        if not isinstance(item, Mapping):
            continue
        action_id = str(item.get("id") or item.get("action_id") or "").strip()
        if not action_id:
            continue
        bindings.append(
            build_interaction_binding(
                action_id,
                target=str(item.get("target") or action_id),
                page_id=page_id,
                requires_confirmation=bool(item.get("requires_confirmation")) or str(item.get("risk_level")) in {"high", "destructive"},
                enabled=bool(item.get("enabled", True)),
            )
        )
    return {
        "schema_version": INTERACTION_BINDINGS_SCHEMA_VERSION,
        "kind": "page_interaction_bindings",
        "page_id": page_id,
        "binding_count": len(bindings),
        "confirmation_count": sum(1 for item in bindings if item["requires_confirmation"]),
        "bindings": bindings,
    }


def validate_interaction_bindings(bindings: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    items = [dict(item) for item in bindings]
    invalid = [item for item in items if item.get("executes_immediately") is True]
    return {
        "schema_version": INTERACTION_BINDINGS_SCHEMA_VERSION,
        "valid": not invalid,
        "binding_count": len(items),
        "invalid_count": len(invalid),
    }


__all__ = ["INTERACTION_BINDINGS_SCHEMA_VERSION", "build_interaction_binding", "build_page_interaction_bindings", "validate_interaction_bindings"]
