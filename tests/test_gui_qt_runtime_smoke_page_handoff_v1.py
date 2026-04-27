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

from media_manager.core.gui_qt_runtime_smoke_page_handoff import build_qt_runtime_smoke_page_handoff


def test_page_handoff_composes_route_nav_registry_and_diagnostics() -> None:
    handoff = build_qt_runtime_smoke_page_handoff(sample_adapter_bundle(), existing_pages=sample_existing_pages())

    assert handoff["kind"] == "qt_runtime_smoke_page_handoff"
    assert handoff["ready_for_shell_registration"] is True
    assert handoff["summary"]["page_count"] == 3
    assert handoff["summary"]["problem_count"] == 0
    assert handoff["summary"]["opens_window"] is False
    assert handoff["summary"]["executes_commands"] is False


def test_page_handoff_not_ready_when_adapter_blocked() -> None:
    handoff = build_qt_runtime_smoke_page_handoff(sample_adapter_bundle(ready=False, problems=1), existing_pages=sample_existing_pages())

    assert handoff["ready_for_shell_registration"] is False
    assert handoff["summary"]["problem_count"] == 1
    assert handoff["navigation_item"]["enabled"] is False
