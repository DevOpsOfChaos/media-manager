from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_PAGE_REGISTRY_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_page_registry(
    route_model: Mapping[str, Any],
    navigation_item: Mapping[str, Any],
    *,
    existing_pages: list[Mapping[str, Any]] | None = None,
) -> dict[str, object]:
    """Build a headless page registry entry for Runtime Smoke."""

    pages = [dict(page) for page in (existing_pages or []) if isinstance(page, Mapping)]
    page_id = str(route_model.get("page_id") or navigation_item.get("page_id") or "runtime-smoke")
    pages = [page for page in pages if page.get("page_id") != page_id and page.get("id") != page_id]
    entry = {
        "page_id": page_id,
        "route_id": route_model.get("route_id"),
        "label": navigation_item.get("label"),
        "enabled": bool(navigation_item.get("enabled")),
        "visible": bool(navigation_item.get("visible", True)),
        "source": "qt_runtime_smoke_adapter",
        "requires_pyside6": False,
        "opens_window": False,
        "executes_commands": False,
        "local_only": True,
    }
    pages.append(entry)
    return {
        "schema_version": QT_RUNTIME_SMOKE_PAGE_REGISTRY_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_page_registry",
        "pages": pages,
        "runtime_smoke_page": entry,
        "summary": {
            "page_count": len(pages),
            "runtime_smoke_registered": any(page.get("page_id") == page_id for page in pages),
            "enabled_page_count": sum(1 for page in pages if page.get("enabled") is not False),
            "local_only_page_count": sum(1 for page in pages if page.get("local_only") is True),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def collect_qt_runtime_smoke_page_ids(registry: Mapping[str, Any]) -> list[str]:
    return [str(page.get("page_id") or page.get("id")) for page in _list(registry.get("pages")) if isinstance(page, Mapping)]


__all__ = [
    "QT_RUNTIME_SMOKE_PAGE_REGISTRY_SCHEMA_VERSION",
    "build_qt_runtime_smoke_page_registry",
    "collect_qt_runtime_smoke_page_ids",
]
