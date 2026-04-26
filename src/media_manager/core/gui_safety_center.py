from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SAFETY_SCHEMA_VERSION = "1.0"


def build_safety_center_state(*, page_model: Mapping[str, Any] | None = None, command_preview: Mapping[str, Any] | None = None) -> dict[str, object]:
    page = page_model or {}
    preview = command_preview or {}
    warnings: list[dict[str, object]] = []
    if page.get("page_id") == "people-review":
        warnings.append({"id": "people_privacy", "level": "warning", "message": "People review data can contain biometric metadata and should stay local."})
    risky_flags = preview.get("risky_flags") if isinstance(preview.get("risky_flags"), list) else []
    for flag in risky_flags:
        warnings.append({"id": f"flag_{flag}", "level": "warning", "message": f"Command preview contains risky flag: {flag}"})
    return {
        "schema_version": SAFETY_SCHEMA_VERSION,
        "kind": "safety_center",
        "warning_count": len(warnings),
        "safe_to_continue": not any(item.get("level") == "error" for item in warnings),
        "messages": warnings,
        "principles": [
            "Preview before apply.",
            "Review before destructive actions.",
            "Keep people data local/private.",
            "The GUI must not execute risky actions without explicit confirmation.",
        ],
    }


__all__ = ["SAFETY_SCHEMA_VERSION", "build_safety_center_state"]
