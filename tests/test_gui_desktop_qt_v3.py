from __future__ import annotations

import json

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    build_qt_desktop_plan,
    qt_desktop_plan_to_pretty_json,
    qt_install_guidance,
    shell_model_to_pretty_json,
    summarize_qt_desktop_plan,
)


def test_desktop_qt_exports_headless_desktop_plan_helpers() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")

    plan = build_qt_desktop_plan(model)
    text = qt_desktop_plan_to_pretty_json(model)
    summary = summarize_qt_desktop_plan(model)

    assert plan["kind"] == "qt_desktop_integration_plan"
    assert json.loads(text)["kind"] == "qt_desktop_integration_plan"
    assert "Qt desktop integration plan" in summary
    assert "Runtime nodes:" in summary


def test_existing_pretty_json_and_guidance_stay_compatible() -> None:
    text = shell_model_to_pretty_json({"b": 1})

    assert '"b": 1' in text
    assert ".[gui]" in qt_install_guidance()
