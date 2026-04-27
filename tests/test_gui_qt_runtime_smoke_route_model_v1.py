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

from media_manager.core.gui_qt_runtime_smoke_route_model import build_qt_runtime_smoke_route_model


def test_route_model_uses_adapter_readiness_and_local_guards() -> None:
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle())

    assert route["route_id"] == "runtime-smoke"
    assert route["page_id"] == "runtime-smoke"
    assert route["enabled"] is True
    assert route["badge"]["state"] == "ready"
    assert route["guards"]["local_only"] is True
    assert route["guards"]["opens_window"] is False
    assert route["guards"]["executes_commands"] is False


def test_route_model_disables_blocked_adapter() -> None:
    route = build_qt_runtime_smoke_route_model(sample_adapter_bundle(ready=False, problems=1))

    assert route["enabled"] is False
    assert route["badge"]["state"] == "blocked"
    assert route["badge"]["problem_count"] == 1
