from __future__ import annotations

from collections.abc import Mapping
from typing import Any

RESOURCE_POLICY_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_resource_policy(*, max_visible_faces: int = 200, max_table_rows: int = 500, max_image_cache_items: int = 1000) -> dict[str, Any]:
    return {
        "schema_version": RESOURCE_POLICY_SCHEMA_VERSION,
        "kind": "qt_resource_policy",
        "max_visible_faces": max(0, int(max_visible_faces)),
        "max_table_rows": max(0, int(max_table_rows)),
        "max_image_cache_items": max(0, int(max_image_cache_items)),
        "lazy_load_images": True,
        "decode_images_on_ui_thread": False,
        "sensitive_asset_warning": True,
    }


def apply_resource_policy_to_page(page_model: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    page = dict(page_model)
    max_faces = int(_as_mapping(policy).get("max_visible_faces", 200) or 0)
    max_rows = int(_as_mapping(policy).get("max_table_rows", 500) or 0)
    if isinstance(page.get("asset_refs"), list):
        page["asset_refs"] = list(page["asset_refs"][:max_faces])
        page["asset_refs_truncated_by_policy"] = len(page_model.get("asset_refs", [])) > len(page["asset_refs"])
    if isinstance(page.get("rows"), list):
        page["rows"] = list(page["rows"][:max_rows])
        page["rows_truncated_by_policy"] = len(page_model.get("rows", [])) > len(page["rows"])
    page["resource_policy"] = dict(policy)
    return page


def summarize_resource_pressure(page_model: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    asset_count = len(page_model.get("asset_refs", [])) if isinstance(page_model.get("asset_refs"), list) else 0
    row_count = len(page_model.get("rows", [])) if isinstance(page_model.get("rows"), list) else 0
    max_faces = int(policy.get("max_visible_faces", 0) or 0)
    max_rows = int(policy.get("max_table_rows", 0) or 0)
    warnings = []
    if max_faces and asset_count > max_faces:
        warnings.append("too_many_visible_faces")
    if max_rows and row_count > max_rows:
        warnings.append("too_many_table_rows")
    return {"asset_count": asset_count, "row_count": row_count, "warnings": warnings, "warning_count": len(warnings)}


__all__ = ["RESOURCE_POLICY_SCHEMA_VERSION", "apply_resource_policy_to_page", "build_qt_resource_policy", "summarize_resource_pressure"]
