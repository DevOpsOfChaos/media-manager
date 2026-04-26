from __future__ import annotations

from collections.abc import Mapping
from typing import Any

CONTENT_SECTIONS_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _section(section_id: str, title: str, *, kind: str = "section", items: list[Any] | None = None, priority: int = 50) -> dict[str, object]:
    return {"id": section_id, "kind": kind, "title": title, "items": list(items or []), "item_count": len(items or []), "priority": priority}


def build_qt_content_sections(page_model: Mapping[str, Any]) -> dict[str, object]:
    kind = str(page_model.get("kind") or "unknown")
    sections: list[dict[str, object]] = []
    if kind == "dashboard_page":
        hero = _mapping(page_model.get("hero"))
        sections.append(_section("hero", str(hero.get("title") or page_model.get("title") or "Dashboard"), kind="hero", items=[dict(hero)], priority=0))
        sections.append(_section("cards", "Cards", kind="card_grid", items=_list(page_model.get("cards")), priority=10))
        sections.append(_section("activity", "Activity", kind="activity", items=[_mapping(page_model.get("activity"))], priority=30))
    elif kind == "people_review_page":
        sections.append(_section("queue", "Review queue", kind="master_list", items=_list(page_model.get("groups")), priority=5))
        sections.append(_section("detail", "Selected person", kind="detail", items=[_mapping(page_model.get("detail"))], priority=10))
        sections.append(_section("assets", "Face assets", kind="asset_grid", items=_list(page_model.get("asset_refs")), priority=20))
    elif kind in {"table_page", "profiles_page"}:
        sections.append(_section("table", str(page_model.get("title") or "Table"), kind="table", items=_list(page_model.get("rows")), priority=10))
    else:
        empty = page_model.get("empty_state")
        sections.append(_section("empty", str(page_model.get("title") or "Empty"), kind="empty_state", items=[empty] if empty else [], priority=99))
    sections.sort(key=lambda item: int(item.get("priority", 50)))
    return {"schema_version": CONTENT_SECTIONS_SCHEMA_VERSION, "page_id": page_model.get("page_id"), "section_count": len(sections), "sections": sections}


__all__ = ["CONTENT_SECTIONS_SCHEMA_VERSION", "build_qt_content_sections"]
