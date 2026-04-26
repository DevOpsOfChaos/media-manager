from __future__ import annotations

from collections.abc import Mapping
from typing import Any

GUI_ACTION_SCHEMA_VERSION = "1.0"


def build_safe_gui_action(action_id: str, label: str, *, page_id: str | None = None, description: str = "", enabled: bool = True) -> dict[str, object]:
    return {
        "schema_version": GUI_ACTION_SCHEMA_VERSION,
        "id": action_id,
        "label": label,
        "description": description,
        "page_id": page_id,
        "enabled": bool(enabled),
        "risk_level": "safe",
        "executes_filesystem_changes": False,
    }


def build_page_actions(page_model: Mapping[str, Any], *, language: str = "en") -> list[dict[str, object]]:
    page_id = str(page_model.get("page_id") or "dashboard")
    if page_id == "people-review":
        return [
            build_safe_gui_action("review_people_groups", "Review people groups", page_id=page_id, description="Open group detail cards and mark faces as included or rejected."),
            build_safe_gui_action("preview_people_apply", "Preview catalog training", page_id=page_id, description="Preview catalog changes before writing embeddings."),
        ]
    if page_id == "new-run":
        return [build_safe_gui_action("create_preview", "Create preview", page_id=page_id, description="Build a non-destructive preview command plan.")]
    return [build_safe_gui_action("refresh", "Refresh", page_id=page_id, description="Reload the current view state.")]


__all__ = ["GUI_ACTION_SCHEMA_VERSION", "build_page_actions", "build_safe_gui_action"]
