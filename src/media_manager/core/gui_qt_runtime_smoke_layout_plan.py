from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_LAYOUT_PLAN_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _columns_for_density(density: str) -> int:
    return {"compact": 1, "comfortable": 2, "spacious": 2}.get(str(density), 2)


def build_qt_runtime_smoke_layout_plan(visible_plan: Mapping[str, Any], *, density: str = "comfortable") -> dict[str, object]:
    """Build deterministic layout placements for the visible runtime smoke plan."""

    sections = [section for section in _list(visible_plan.get("sections")) if isinstance(section, Mapping)]
    columns = _columns_for_density(density)
    placements: list[dict[str, object]] = []
    for index, section in enumerate(sections):
        section_id = str(section.get("id") or f"section-{index + 1}")
        component = str(section.get("component") or "Section")
        if component in {"StatusBanner", "ActionBar"}:
            row = len(placements)
            placements.append({"section_id": section_id, "row": row, "column": 0, "column_span": columns, "component": component})
        else:
            logical_index = sum(1 for placement in placements if placement["component"] not in {"StatusBanner", "ActionBar"})
            placements.append(
                {
                    "section_id": section_id,
                    "row": 1 + logical_index // columns,
                    "column": logical_index % columns,
                    "column_span": 1,
                    "component": component,
                }
            )
    return {
        "schema_version": QT_RUNTIME_SMOKE_LAYOUT_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_layout_plan",
        "page_id": visible_plan.get("page_id"),
        "density": density,
        "columns": columns,
        "placements": placements,
        "summary": {
            "placement_count": len(placements),
            "full_width_count": sum(1 for placement in placements if int(placement.get("column_span") or 0) == columns),
            "section_count": len(sections),
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


__all__ = ["QT_RUNTIME_SMOKE_LAYOUT_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_layout_plan"]
