from __future__ import annotations

import json

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    attach_guarded_qt_runtime_smoke_to_shell_model,
    build_guarded_qt_runtime_smoke_plan,
    guarded_qt_runtime_smoke_plan_to_pretty_json,
    summarize_guarded_qt_runtime_smoke_plan,
)


def test_desktop_qt_exports_guarded_runtime_smoke_helpers() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")

    plan = build_guarded_qt_runtime_smoke_plan(model)
    text = guarded_qt_runtime_smoke_plan_to_pretty_json(model)
    summary = summarize_guarded_qt_runtime_smoke_plan(model)

    assert plan["kind"] == "guarded_qt_runtime_smoke_integration"
    assert json.loads(text)["page_id"] == "runtime-smoke"
    assert "Guarded Qt Runtime Smoke integration" in summary
    assert "Opens window now: False" in summary


def test_desktop_qt_attach_helper_activates_runtime_smoke() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")

    updated = attach_guarded_qt_runtime_smoke_to_shell_model(model, activate=True)

    assert updated["active_page_id"] == "runtime-smoke"
    assert updated["page"]["kind"] == "qt_runtime_smoke_page_model"
