from __future__ import annotations

from media_manager.core.gui_shell_model import build_gui_shell_model, summarize_gui_shell_model


def test_shell_model_active_runtime_smoke_builds_guarded_page() -> None:
    model = build_gui_shell_model(active_page_id="runtime-smoke", language="en")

    assert model["active_page_id"] == "runtime-smoke"
    assert model["page"]["kind"] == "qt_runtime_smoke_page_model"
    assert any(item["id"] == "runtime-smoke" and item["active"] for item in model["navigation"])
    assert model["runtime_smoke"]["summary"]["ready_for_shell_route"] is True


def test_shell_summary_mentions_runtime_smoke_page() -> None:
    model = build_gui_shell_model(active_page_id="runtime-smoke")

    text = summarize_gui_shell_model(model)

    assert "Active page: runtime-smoke" in text
    assert "Runtime Smoke" in text
