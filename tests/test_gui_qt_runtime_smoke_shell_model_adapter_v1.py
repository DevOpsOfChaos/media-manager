from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_qt_runtime_smoke_shell_model_adapter import (
    apply_guarded_qt_runtime_smoke_to_shell_model,
    summarize_runtime_smoke_shell_attachment,
)
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_shell_model_adapter_adds_runtime_smoke_navigation_and_palette_items() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")
    integration = build_guarded_qt_runtime_smoke_integration(model)

    updated = apply_guarded_qt_runtime_smoke_to_shell_model(model, integration)

    nav_ids = [item["id"] for item in updated["navigation"]]
    palette_ids = [item["id"] for item in updated["command_palette"]["items"]]
    assert nav_ids.count("runtime-smoke") == 1
    assert "runtime-smoke.open" in palette_ids
    assert updated["runtime_smoke"]["summary"]["ready_for_shell_route"] is True


def test_shell_model_adapter_can_activate_runtime_smoke_page() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")
    integration = build_guarded_qt_runtime_smoke_integration(model)

    updated = apply_guarded_qt_runtime_smoke_to_shell_model(model, integration, activate=True)
    summary = summarize_runtime_smoke_shell_attachment(updated)

    assert updated["active_page_id"] == "runtime-smoke"
    assert updated["page"]["kind"] == "qt_runtime_smoke_page_model"
    assert any(item["id"] == "runtime-smoke" and item["active"] for item in updated["navigation"])
    assert summary["attached"] is True
    assert summary["executes_commands"] is False
