from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SAFETY_BANNER_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_safety_banner(shell_model: Mapping[str, Any]) -> dict[str, object]:
    safety = _as_mapping(shell_model.get("safety_center"))
    status = _as_mapping(shell_model.get("status_bar"))
    page = _as_mapping(shell_model.get("page"))
    page_id = str(shell_model.get("active_page_id") or page.get("page_id") or "dashboard")
    privacy_text = str(status.get("privacy") or "People data stays local.")
    people_page = page_id in {"people", "people-review"}
    has_sensitive_assets = bool(page.get("asset_refs")) or bool(_as_mapping(page.get("overview")).get("sensitive"))
    severity = "warning" if people_page or has_sensitive_assets else "info"
    visible = people_page or has_sensitive_assets or bool(safety.get("warnings"))
    return {
        "schema_version": SAFETY_BANNER_SCHEMA_VERSION,
        "kind": "safety_banner",
        "visible": visible,
        "severity": severity,
        "title": "Local privacy reminder" if visible else "Safe preview mode",
        "message": privacy_text if visible else "The GUI models do not execute commands directly.",
        "page_id": page_id,
        "dismissible": not people_page,
    }


__all__ = ["SAFETY_BANNER_SCHEMA_VERSION", "build_safety_banner"]
