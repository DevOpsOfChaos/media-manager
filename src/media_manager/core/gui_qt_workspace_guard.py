from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WORKSPACE_GUARD_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_workspace_guard(workbench_state: Mapping[str, Any]) -> dict[str, Any]:
    save_state = _as_mapping(workbench_state.get("save_state"))
    apply_preview = _as_mapping(workbench_state.get("apply_preview"))
    problems: list[str] = []
    warnings: list[str] = []
    if not save_state.get("has_workspace_path"):
        warnings.append("workspace_path_missing")
    if save_state.get("has_unsaved_changes"):
        warnings.append("unsaved_changes")
    if apply_preview.get("blocked_reasons"):
        problems.extend(str(item) for item in apply_preview.get("blocked_reasons", []))
    return {
        "schema_version": WORKSPACE_GUARD_SCHEMA_VERSION,
        "kind": "qt_workspace_guard",
        "problems": problems,
        "warnings": warnings,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "can_close_without_prompt": not save_state.get("has_unsaved_changes"),
        "can_apply": not problems and bool(apply_preview.get("safe_to_apply")),
    }


__all__ = ["WORKSPACE_GUARD_SCHEMA_VERSION", "build_workspace_guard"]
