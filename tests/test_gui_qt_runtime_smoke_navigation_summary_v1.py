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

from media_manager.core.gui_qt_runtime_smoke_navigation_summary import summarize_qt_runtime_smoke_page_handoff
from media_manager.core.gui_qt_runtime_smoke_page_handoff import build_qt_runtime_smoke_page_handoff


def test_navigation_summary_mentions_safety_flags() -> None:
    handoff = build_qt_runtime_smoke_page_handoff(sample_adapter_bundle(), existing_pages=sample_existing_pages())
    text = summarize_qt_runtime_smoke_page_handoff(handoff)

    assert "Ready for shell registration: True" in text
    assert "Opens window: False" in text
    assert "Executes commands: False" in text
