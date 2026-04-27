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
from media_manager.core.gui_qt_runtime_smoke_route_model import build_qt_runtime_smoke_route_model
from media_manager.core.gui_qt_runtime_smoke_route_validator import validate_qt_runtime_smoke_route


def test_route_validator_accepts_safe_route_and_navigation_item() -> None:
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle())
    nav = build_qt_runtime_smoke_navigation_item(route)
    validation = validate_qt_runtime_smoke_route(route, nav)

    assert validation["valid"] is True
    assert validation["problem_count"] == 0
    assert validation["summary"]["local_only"] is True


def test_route_validator_rejects_page_id_mismatch() -> None:
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle())
    nav = build_qt_runtime_smoke_navigation_item(route)
    nav["page_id"] = "other"
    validation = validate_qt_runtime_smoke_route(route, nav)

    assert validation["valid"] is False
    assert validation["problems"][0]["code"] == "page_id_mismatch"
