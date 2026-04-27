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

from media_manager.core.gui_qt_runtime_smoke_diagnostics import build_qt_runtime_smoke_diagnostics
from media_manager.core.gui_qt_runtime_smoke_navigation_item import build_qt_runtime_smoke_navigation_item
from media_manager.core.gui_qt_runtime_smoke_route_model import build_qt_runtime_smoke_route_model
from media_manager.core.gui_qt_runtime_smoke_route_validator import validate_qt_runtime_smoke_route


def test_diagnostics_combines_adapter_and_route_readiness() -> None:
    bundle = sample_adapter_bundle()
    route = build_qt_runtime_smoke_route_model(bundle)
    nav = build_qt_runtime_smoke_navigation_item(route)
    route_validation = validate_qt_runtime_smoke_route(route, nav)
    diagnostics = build_qt_runtime_smoke_diagnostics(bundle, route_validation)

    assert diagnostics["ready"] is True
    assert diagnostics["summary"]["total_problem_count"] == 0
    assert diagnostics["adapter"]["render_step_count"] == 9
    assert diagnostics["route"]["local_only"] is True


def test_diagnostics_reports_adapter_problem_count() -> None:
    bundle = sample_adapter_bundle(ready=False, problems=2)
    route = build_qt_runtime_smoke_route_model(bundle)
    nav = build_qt_runtime_smoke_navigation_item(route)
    diagnostics = build_qt_runtime_smoke_diagnostics(bundle, validate_qt_runtime_smoke_route(route, nav))

    assert diagnostics["ready"] is False
    assert diagnostics["summary"]["total_problem_count"] == 2
