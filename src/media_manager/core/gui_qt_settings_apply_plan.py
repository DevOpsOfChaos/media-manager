from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SETTINGS_APPLY_PLAN_SCHEMA_VERSION = "1.0"
_RESTART_KEYS = {"language", "theme", "density"}
_SENSITIVE_KEYS = {"people_privacy_acknowledged", "last_catalog_path"}


def build_settings_apply_plan(current: Mapping[str, Any], desired: Mapping[str, Any]) -> dict[str, object]:
    changes = []
    keys = sorted(set(current.keys()) | set(desired.keys()))
    for key in keys:
        old = current.get(key)
        new = desired.get(key)
        if old != new:
            changes.append(
                {
                    "key": key,
                    "old_value": old,
                    "new_value": new,
                    "requires_ui_refresh": key in _RESTART_KEYS,
                    "sensitive": key in _SENSITIVE_KEYS,
                }
            )
    return {
        "schema_version": SETTINGS_APPLY_PLAN_SCHEMA_VERSION,
        "kind": "qt_settings_apply_plan",
        "change_count": len(changes),
        "requires_ui_refresh": any(change["requires_ui_refresh"] for change in changes),
        "sensitive_change_count": sum(1 for change in changes if change["sensitive"]),
        "can_apply": True,
        "executes_immediately": False,
        "changes": changes,
    }


__all__ = ["SETTINGS_APPLY_PLAN_SCHEMA_VERSION", "build_settings_apply_plan"]
