from __future__ import annotations

from collections.abc import Mapping
from typing import Any

COMMAND_CENTER_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


_DEFAULT_COMMANDS = [
    {"id": "open-dashboard", "label": "Open dashboard", "group": "navigation", "target_page_id": "dashboard"},
    {"id": "open-people-review", "label": "Open people review", "group": "navigation", "target_page_id": "people-review"},
    {"id": "open-run-history", "label": "Open run history", "group": "navigation", "target_page_id": "run-history"},
    {"id": "open-profiles", "label": "Open profiles", "group": "navigation", "target_page_id": "profiles"},
    {"id": "open-settings", "label": "Open settings", "group": "navigation", "target_page_id": "settings"},
]


def normalize_command_center_row(row: Mapping[str, Any], *, index: int = 0) -> dict[str, object]:
    command_id = str(row.get("id") or f"command-{index + 1}")
    label = str(row.get("label") or command_id.replace("-", " ").title())
    risk_level = str(row.get("risk_level") or "safe")
    requires_confirmation = bool(row.get("requires_confirmation", risk_level in {"high", "destructive"}))
    return {
        "schema_version": COMMAND_CENTER_SCHEMA_VERSION,
        "id": command_id,
        "label": label,
        "group": str(row.get("group") or "general"),
        "target_page_id": row.get("target_page_id"),
        "enabled": bool(row.get("enabled", True)),
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation,
        "executes_immediately": False,
    }


def build_command_center(commands: list[Mapping[str, Any]] | None = None, *, query: str = "") -> dict[str, object]:
    source = commands if commands is not None else _DEFAULT_COMMANDS
    rows = [normalize_command_center_row(_as_mapping(item), index=index) for index, item in enumerate(source)]
    q = query.strip().casefold()
    if q:
        rows = [row for row in rows if q in str(row["label"]).casefold() or q in str(row["id"]).casefold()]
    groups: dict[str, int] = {}
    for row in rows:
        group = str(row["group"])
        groups[group] = groups.get(group, 0) + 1
    return {
        "schema_version": COMMAND_CENTER_SCHEMA_VERSION,
        "kind": "command_center",
        "query": query,
        "row_count": len(rows),
        "confirmation_count": sum(1 for row in rows if row["requires_confirmation"]),
        "groups": dict(sorted(groups.items())),
        "rows": rows,
    }


def command_center_to_intent(row: Mapping[str, Any]) -> dict[str, object]:
    target = row.get("target_page_id")
    return {
        "schema_version": COMMAND_CENTER_SCHEMA_VERSION,
        "intent_type": "navigate" if target else "noop",
        "target_page_id": target,
        "source_command_id": row.get("id"),
        "requires_confirmation": bool(row.get("requires_confirmation", False)),
        "executes_immediately": False,
    }


__all__ = [
    "COMMAND_CENTER_SCHEMA_VERSION",
    "build_command_center",
    "command_center_to_intent",
    "normalize_command_center_row",
]
