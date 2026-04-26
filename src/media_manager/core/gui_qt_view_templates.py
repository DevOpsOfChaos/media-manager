from __future__ import annotations

from collections.abc import Mapping
from typing import Any

VIEW_TEMPLATE_SCHEMA_VERSION = "1.0"

_TEMPLATE_REGISTRY: dict[str, dict[str, object]] = {
    "dashboard": {
        "template_id": "dashboard",
        "layout": "hero_metrics_activity",
        "regions": ["header", "hero", "metric_cards", "activity", "footer"],
        "primary_component": "dashboard_grid",
    },
    "people-review": {
        "template_id": "people-review",
        "layout": "review_master_detail_gallery",
        "regions": ["header", "queue", "detail", "face_gallery", "apply_bar"],
        "primary_component": "people_review_workbench",
    },
    "run-history": {
        "template_id": "run-history",
        "layout": "table_with_filters",
        "regions": ["header", "filters", "table", "detail_drawer"],
        "primary_component": "run_history_table",
    },
    "profiles": {
        "template_id": "profiles",
        "layout": "cards_with_editor",
        "regions": ["header", "profile_cards", "editor", "validation"],
        "primary_component": "profile_workspace",
    },
    "settings": {
        "template_id": "settings",
        "layout": "settings_sections",
        "regions": ["header", "sections", "diagnostics", "footer"],
        "primary_component": "settings_workspace",
    },
}

_ALIASES = {
    "people": "people-review",
    "runs": "run-history",
    "doctor": "settings",
    "new run": "new-run",
}


def normalize_template_id(page_id: str | None) -> str:
    value = str(page_id or "dashboard").strip().lower()
    return _ALIASES.get(value, value)


def get_view_template(page_id: str | None) -> dict[str, object]:
    normalized = normalize_template_id(page_id)
    template = dict(_TEMPLATE_REGISTRY.get(normalized, {
        "template_id": normalized,
        "layout": "generic_page",
        "regions": ["header", "content", "footer"],
        "primary_component": "generic_content",
    }))
    template["schema_version"] = VIEW_TEMPLATE_SCHEMA_VERSION
    template["page_id"] = normalized
    return template


def build_view_template_catalog() -> dict[str, object]:
    return {
        "schema_version": VIEW_TEMPLATE_SCHEMA_VERSION,
        "template_count": len(_TEMPLATE_REGISTRY),
        "templates": [get_view_template(page_id) for page_id in sorted(_TEMPLATE_REGISTRY)],
        "aliases": dict(sorted(_ALIASES.items())),
    }


def validate_page_against_template(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "dashboard")
    template = get_view_template(page_id)
    required_regions = list(template.get("regions", []))
    missing_regions: list[str] = []
    if "header" in required_regions and not page_model.get("title"):
        missing_regions.append("header")
    if page_id == "people-review" and "groups" not in page_model:
        missing_regions.append("queue")
    if page_id in {"run-history", "profiles"} and "rows" not in page_model:
        missing_regions.append("table")
    return {
        "schema_version": VIEW_TEMPLATE_SCHEMA_VERSION,
        "page_id": normalize_template_id(page_id),
        "template_id": template["template_id"],
        "valid": not missing_regions,
        "missing_regions": missing_regions,
        "layout": template["layout"],
    }


__all__ = [
    "VIEW_TEMPLATE_SCHEMA_VERSION",
    "build_view_template_catalog",
    "get_view_template",
    "normalize_template_id",
    "validate_page_against_template",
]
