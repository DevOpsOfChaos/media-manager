from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_READINESS_SCHEMA_VERSION = "1.0"
REQUIRED_KEYS_BY_KIND = {
    "dashboard_page": ("hero", "cards"),
    "people_review_page": ("queue", "detail", "editor"),
    "table_page": ("columns", "rows"),
    "profiles_page": ("columns", "rows", "profile_editor"),
    "settings_page": ("sections",),
}


def evaluate_qt_page_readiness(page_model: Mapping[str, Any]) -> dict[str, object]:
    kind = str(page_model.get("kind") or "unknown")
    required = REQUIRED_KEYS_BY_KIND.get(kind, ("title",))
    missing = [key for key in required if key not in page_model]
    warnings = []
    if not page_model.get("title"):
        warnings.append("missing_title")
    if page_model.get("empty_state") and kind != "people_review_page":
        warnings.append("empty_state_visible")
    score = max(0, 100 - (len(missing) * 30) - (len(warnings) * 10))
    return {
        "schema_version": PAGE_READINESS_SCHEMA_VERSION,
        "kind": "qt_page_readiness",
        "page_id": page_model.get("page_id"),
        "page_kind": kind,
        "ready": not missing,
        "score": score,
        "missing": missing,
        "warnings": warnings,
        "required_keys": list(required),
    }


def summarize_qt_page_readiness(items: list[Mapping[str, Any]]) -> dict[str, object]:
    ready_count = sum(1 for item in items if bool(item.get("ready")))
    return {
        "schema_version": PAGE_READINESS_SCHEMA_VERSION,
        "kind": "qt_page_readiness_summary",
        "page_count": len(items),
        "ready_count": ready_count,
        "blocked_count": len(items) - ready_count,
        "average_score": round(sum(int(item.get("score", 0)) for item in items) / len(items), 2) if items else 0,
    }


__all__ = ["PAGE_READINESS_SCHEMA_VERSION", "REQUIRED_KEYS_BY_KIND", "evaluate_qt_page_readiness", "summarize_qt_page_readiness"]
