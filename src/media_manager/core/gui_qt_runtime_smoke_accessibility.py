from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ACCESSIBILITY_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_accessibility_plan(visible_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build accessibility labels and tab order for the visible smoke plan."""

    sections = [section for section in _list(visible_plan.get("sections")) if isinstance(section, Mapping)]
    labels = []
    tab_order = []
    for index, section in enumerate(sections):
        section_id = str(section.get("id") or f"section-{index + 1}")
        title = str(section.get("title") or section_id)
        component = str(section.get("component") or "Section")
        labels.append(
            {
                "target_id": section_id,
                "label": title,
                "role": {
                    "StatusBanner": "status",
                    "DataTable": "table",
                    "DetailPanel": "group",
                    "ActionBar": "toolbar",
                }.get(component, "group"),
            }
        )
        tab_order.append({"target_id": section_id, "order": index + 1})
    summary = _mapping(visible_plan.get("summary"))
    if summary.get("contains_sensitive_people_data_possible"):
        labels.append(
            {
                "target_id": "runtime-smoke-privacy-notice",
                "label": "People Review may contain sensitive local-only data.",
                "role": "note",
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_ACCESSIBILITY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_accessibility_plan",
        "page_id": visible_plan.get("page_id"),
        "labels": labels,
        "tab_order": tab_order,
        "summary": {
            "label_count": len(labels),
            "tab_stop_count": len(tab_order),
            "has_privacy_notice": any(label.get("target_id") == "runtime-smoke-privacy-notice" for label in labels),
            "opens_window": False,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_ACCESSIBILITY_SCHEMA_VERSION", "build_qt_runtime_smoke_accessibility_plan"]
