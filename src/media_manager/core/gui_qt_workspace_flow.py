from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WORKSPACE_FLOW_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_workspace_flow(workbench_state: Mapping[str, Any]) -> dict[str, Any]:
    save_state = _as_mapping(workbench_state.get("save_state"))
    guard = _as_mapping(workbench_state.get("guard"))
    apply_preview = _as_mapping(workbench_state.get("apply_preview"))
    steps = [
        {"id": "load_workspace", "label": "Load workspace", "complete": bool(save_state.get("has_workspace_path"))},
        {"id": "review_changes", "label": "Review pending changes", "complete": int(save_state.get("pending_change_count", 0)) > 0},
        {"id": "save_workspace", "label": "Save workspace", "complete": not save_state.get("has_unsaved_changes")},
        {"id": "preview_apply", "label": "Preview catalog apply", "complete": bool(apply_preview)},
        {"id": "apply_ready", "label": "Apply ready groups", "complete": bool(apply_preview.get("safe_to_apply"))},
    ]
    next_step = next((step for step in steps if not step["complete"]), steps[-1])
    return {
        "schema_version": WORKSPACE_FLOW_SCHEMA_VERSION,
        "kind": "qt_workspace_flow",
        "steps": steps,
        "step_count": len(steps),
        "complete_count": sum(1 for step in steps if step["complete"]),
        "next_step_id": next_step["id"],
        "blocked": int(guard.get("problem_count", 0)) > 0,
        "blocked_reasons": list(guard.get("problems", [])) if isinstance(guard.get("problems"), list) else [],
    }


__all__ = ["WORKSPACE_FLOW_SCHEMA_VERSION", "build_workspace_flow"]
