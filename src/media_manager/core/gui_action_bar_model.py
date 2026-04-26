from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ACTION_BAR_SCHEMA_VERSION = "1.0"

_BUCKET_ORDER = ("primary", "secondary", "danger", "disabled")


def _normalize_action(action: Mapping[str, Any]) -> dict[str, object]:
    enabled = bool(action.get("enabled", True))
    risk = str(action.get("risk_level") or "safe")
    variant = str(action.get("variant") or ("danger" if risk in {"high", "destructive"} else "primary" if action.get("recommended") else "secondary"))
    if not enabled:
        variant = "disabled"
    return {
        "id": str(action.get("id") or "action"),
        "label": str(action.get("label") or action.get("id") or "Action"),
        "enabled": enabled,
        "recommended": bool(action.get("recommended", False)),
        "requires_confirmation": bool(action.get("requires_confirmation", False)),
        "risk_level": risk,
        "variant": variant,
        "blocked_reason": action.get("blocked_reason"),
    }


def build_action_bar(
    actions: Iterable[Mapping[str, Any]],
    *,
    max_primary: int = 2,
    label: str = "Actions",
) -> dict[str, object]:
    normalized = [_normalize_action(action) for action in actions]
    primary_seen = 0
    for action in normalized:
        if action["variant"] == "primary":
            primary_seen += 1
            if primary_seen > max(0, int(max_primary)):
                action["variant"] = "secondary"
    buckets = {bucket: [] for bucket in _BUCKET_ORDER}
    for action in normalized:
        buckets.setdefault(str(action["variant"]), []).append(action)
    return {
        "schema_version": ACTION_BAR_SCHEMA_VERSION,
        "kind": "action_bar",
        "label": label,
        "actions": normalized,
        "action_count": len(normalized),
        "enabled_count": sum(1 for action in normalized if action["enabled"]),
        "confirmation_count": sum(1 for action in normalized if action["requires_confirmation"]),
        "buckets": buckets,
    }


def recommended_action(action_bar: Mapping[str, Any]) -> dict[str, object] | None:
    actions = action_bar.get("actions")
    if not isinstance(actions, list):
        return None
    for action in actions:
        if isinstance(action, Mapping) and action.get("enabled") and action.get("recommended"):
            return dict(action)
    for action in actions:
        if isinstance(action, Mapping) and action.get("enabled"):
            return dict(action)
    return None


__all__ = ["ACTION_BAR_SCHEMA_VERSION", "build_action_bar", "recommended_action"]
