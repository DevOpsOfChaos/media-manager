from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DIFF_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def diff_mapping(before: Mapping[str, Any], after: Mapping[str, Any], *, path: str = "") -> list[dict[str, object]]:
    changes: list[dict[str, object]] = []
    keys = sorted(set(before) | set(after))
    for key in keys:
        current_path = f"{path}.{key}" if path else str(key)
        if key not in before:
            changes.append({"path": current_path, "change": "added", "before": None, "after": after[key]})
            continue
        if key not in after:
            changes.append({"path": current_path, "change": "removed", "before": before[key], "after": None})
            continue
        left = before[key]
        right = after[key]
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            changes.extend(diff_mapping(left, right, path=current_path))
        elif left != right:
            changes.append({"path": current_path, "change": "changed", "before": left, "after": right})
    return changes


def build_model_diff(before: Mapping[str, Any], after: Mapping[str, Any], *, max_changes: int = 200) -> dict[str, object]:
    all_changes = diff_mapping(_mapping(before), _mapping(after))
    limit = max(0, int(max_changes))
    returned = all_changes[:limit]
    by_type: dict[str, int] = {}
    for item in all_changes:
        change = str(item.get("change"))
        by_type[change] = by_type.get(change, 0) + 1
    return {
        "schema_version": DIFF_SCHEMA_VERSION,
        "kind": "gui_model_diff",
        "change_count": len(all_changes),
        "returned_change_count": len(returned),
        "truncated": len(all_changes) > len(returned),
        "change_summary": dict(sorted(by_type.items())),
        "changes": returned,
    }


def diff_has_changes(diff_payload: Mapping[str, Any]) -> bool:
    count = diff_payload.get("change_count")
    return isinstance(count, int) and count > 0


__all__ = ["DIFF_SCHEMA_VERSION", "build_model_diff", "diff_has_changes", "diff_mapping"]
