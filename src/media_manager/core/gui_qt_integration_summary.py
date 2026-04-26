from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_INTEGRATION_SUMMARY_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_integration_summary(
    *,
    desktop_plan: Mapping[str, Any] | None = None,
    factory_plan: Mapping[str, Any] | None = None,
    diagnostics: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    desktop_plan = desktop_plan or {}
    factory_plan = factory_plan or {}
    diagnostics = diagnostics or {}
    page_plan = _as_mapping(desktop_plan.get("page_plan"))
    return {
        "schema_version": QT_INTEGRATION_SUMMARY_SCHEMA_VERSION,
        "kind": "qt_integration_summary",
        "active_page_id": desktop_plan.get("active_page_id") or page_plan.get("page_id"),
        "page_plan_kind": page_plan.get("kind"),
        "widget_count": factory_plan.get("widget_count", 0),
        "unsupported_widget_count": factory_plan.get("unsupported_widget_count", 0),
        "valid": bool(diagnostics.get("valid", True)) and int(factory_plan.get("unsupported_widget_count", 0) or 0) == 0,
        "problem_count": diagnostics.get("problem_count", 0),
        "warning_count": diagnostics.get("warning_count", 0),
        "ready_for_manual_qt_smoke": bool(desktop_plan) and bool(factory_plan) and bool(diagnostics.get("valid", True)),
    }


__all__ = ["QT_INTEGRATION_SUMMARY_SCHEMA_VERSION", "build_qt_integration_summary"]
