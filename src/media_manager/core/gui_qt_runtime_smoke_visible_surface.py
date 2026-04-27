from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_accessibility import build_qt_runtime_smoke_accessibility_plan
from .gui_qt_runtime_smoke_layout_plan import build_qt_runtime_smoke_layout_plan
from .gui_qt_runtime_smoke_visible_plan import build_qt_runtime_smoke_visible_plan

QT_RUNTIME_SMOKE_VISIBLE_SURFACE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_visible_surface(page_model: Mapping[str, Any], *, density: str = "comfortable") -> dict[str, object]:
    """Compose the full visible-surface contract for the runtime smoke page."""

    visible_plan = build_qt_runtime_smoke_visible_plan(page_model)
    layout_plan = build_qt_runtime_smoke_layout_plan(visible_plan, density=density)
    accessibility = build_qt_runtime_smoke_accessibility_plan(visible_plan)
    visible_summary = _mapping(visible_plan.get("summary"))
    layout_summary = _mapping(layout_plan.get("summary"))
    accessibility_summary = _mapping(accessibility.get("summary"))
    ready = (
        bool(visible_summary.get("local_only", True))
        and bool(page_model.get("capabilities", {}).get("executes_commands") is False if isinstance(page_model.get("capabilities"), Mapping) else True)
        and int(layout_summary.get("placement_count") or 0) == int(visible_summary.get("section_count") or 0)
    )
    return {
        "schema_version": QT_RUNTIME_SMOKE_VISIBLE_SURFACE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_visible_surface",
        "page_id": visible_plan.get("page_id"),
        "active_page_id": visible_plan.get("active_page_id"),
        "visible_plan": visible_plan,
        "layout_plan": layout_plan,
        "accessibility": accessibility,
        "summary": {
            "section_count": visible_summary.get("section_count", 0),
            "placement_count": layout_summary.get("placement_count", 0),
            "label_count": accessibility_summary.get("label_count", 0),
            "ready_for_runtime_review": visible_summary.get("ready_for_runtime_review", False),
            "has_privacy_notice": accessibility_summary.get("has_privacy_notice", False),
            "ready_for_qt_adapter": ready,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready_for_qt_adapter": ready,
    }


__all__ = ["QT_RUNTIME_SMOKE_VISIBLE_SURFACE_SCHEMA_VERSION", "build_qt_runtime_smoke_visible_surface"]
