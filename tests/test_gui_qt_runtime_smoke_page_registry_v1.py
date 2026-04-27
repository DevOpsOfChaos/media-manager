from __future__ import annotations


def sample_adapter_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_adapter_bundle",
        "page_id": "runtime-smoke",
        "ready_for_qt_runtime": ready,
        "visible_surface": {
            "page_id": "runtime-smoke",
            "active_page_id": "people-review",
            "summary": {"local_only": True, "ready_for_runtime_review": ready},
        },
        "validation": {"valid": ready, "problem_count": problems, "summary": {"render_step_count": 9, "binding_count": 2, "event_count": 2, "local_only": True}},
        "summary": {"ready_for_qt_runtime": ready, "render_step_count": 9, "binding_count": 2, "event_count": 2, "problem_count": problems, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }


def sample_existing_pages() -> list[dict[str, object]]:
    return [
        {"page_id": "dashboard", "label": "Dashboard", "enabled": True, "local_only": True},
        {"page_id": "people-review", "label": "People Review", "enabled": True, "local_only": True},
    ]

from media_manager.core.gui_qt_runtime_smoke_navigation_item import build_qt_runtime_smoke_navigation_item
from media_manager.core.gui_qt_runtime_smoke_page_registry import build_qt_runtime_smoke_page_registry, collect_qt_runtime_smoke_page_ids
from media_manager.core.gui_qt_runtime_smoke_route_model import build_qt_runtime_smoke_route_model


def test_page_registry_adds_runtime_smoke_page_once() -> None:
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle())
    nav = build_qt_runtime_smoke_navigation_item(route)
    registry = build_qt_runtime_smoke_page_registry(route, nav, existing_pages=sample_existing_pages())

    assert registry["summary"]["page_count"] == 3
    assert registry["summary"]["runtime_smoke_registered"] is True
    assert collect_qt_runtime_smoke_page_ids(registry) == ["dashboard", "people-review", "runtime-smoke"]


def test_page_registry_replaces_existing_runtime_smoke_entry() -> None:
    pages = [*sample_existing_pages(), {"page_id": "runtime-smoke", "label": "Old", "enabled": False}]
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle())
    nav = build_qt_runtime_smoke_navigation_item(route)
    registry = build_qt_runtime_smoke_page_registry(route, nav, existing_pages=pages)

    assert collect_qt_runtime_smoke_page_ids(registry).count("runtime-smoke") == 1
    assert registry["runtime_smoke_page"]["enabled"] is True
