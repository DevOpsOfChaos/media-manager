from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_command_palette_and_toolbar_bindings_are_deferred() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    palette = bundle["command_palette_binding"]
    toolbar = bundle["toolbar_binding"]

    assert palette["summary"]["item_count"] == 4
    assert palette["summary"]["immediate_execution_count"] == 0
    assert toolbar["summary"]["button_count"] == 3
    assert toolbar["summary"]["confirmation_button_count"] == 1
    assert all(item["executes_immediately"] is False for item in palette["items"])
    assert all(button["executes_immediately"] is False for button in toolbar["buttons"])


def test_action_registry_merges_navigation_and_commands() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    registry = bundle["action_registry"]

    action_ids = {item["id"] for item in registry["actions"]}
    assert "navigate_runtime-smoke" in action_ids
    assert "runtime-smoke.start-manual-smoke" in action_ids
    assert registry["summary"]["immediate_execution_count"] == 0
