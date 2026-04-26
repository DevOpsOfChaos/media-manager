from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

CHANGE_SUMMARY_SCHEMA_VERSION = "1.0"


def build_change_summary(changes: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = [dict(item) for item in changes]
    by_action: dict[str, int] = {}
    by_target: dict[str, int] = {}
    high_risk = 0
    for item in items:
        action = str(item.get("action_id") or "unknown")
        target_type = str(item.get("target_type") or "unknown")
        by_action[action] = by_action.get(action, 0) + 1
        by_target[target_type] = by_target.get(target_type, 0) + 1
        if item.get("risk_level") == "high" or item.get("requires_confirmation") is True:
            high_risk += 1
    return {
        "schema_version": CHANGE_SUMMARY_SCHEMA_VERSION,
        "change_count": len(items),
        "high_risk_count": high_risk,
        "safe_change_count": max(0, len(items) - high_risk),
        "by_action": dict(sorted(by_action.items())),
        "by_target_type": dict(sorted(by_target.items())),
        "has_changes": bool(items),
        "needs_confirmation": high_risk > 0,
    }


__all__ = ["CHANGE_SUMMARY_SCHEMA_VERSION", "build_change_summary"]
