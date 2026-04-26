from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

PROFILE_WORKBENCH_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_profile_workbench(profiles: Iterable[Mapping[str, Any]], *, selected_profile_id: str | None = None) -> dict[str, object]:
    items = []
    for raw in profiles:
        item = _mapping(raw)
        profile_id = str(item.get("profile_id") or item.get("id") or item.get("title") or "profile")
        items.append(
            {
                "profile_id": profile_id,
                "title": str(item.get("title") or profile_id),
                "command": str(item.get("command") or ""),
                "favorite": bool(item.get("favorite", False)),
                "valid": bool(item.get("valid", True)),
                "selected": profile_id == selected_profile_id,
                "problem_count": int(item.get("problem_count", 0) or 0),
            }
        )
    if selected_profile_id is None and items:
        items[0]["selected"] = True
        selected_profile_id = str(items[0]["profile_id"])
    selected = next((item for item in items if item["selected"]), None)
    return {
        "schema_version": PROFILE_WORKBENCH_SCHEMA_VERSION,
        "kind": "qt_profile_workbench",
        "profile_count": len(items),
        "favorite_count": sum(1 for item in items if item["favorite"]),
        "invalid_count": sum(1 for item in items if not item["valid"]),
        "selected_profile_id": selected_profile_id,
        "selected_profile": selected,
        "profiles": items,
        "empty_state": None if items else {"title": "No profiles", "description": "Create a profile to start faster next time."},
    }


__all__ = ["PROFILE_WORKBENCH_SCHEMA_VERSION", "build_profile_workbench"]
