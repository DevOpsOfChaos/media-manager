from __future__ import annotations

from media_manager.core.gui_shell_model import build_gui_shell_model, summarize_gui_shell_model


def test_gui_shell_model_is_modern_and_bilingual() -> None:
    model = build_gui_shell_model(active_page_id="dashboard", language="de", theme="modern-light")
    assert model["language"] == "de"
    assert model["theme"]["theme"] == "modern-light"
    assert model["capabilities"]["qt_shell"] is True
    assert model["capabilities"]["tkinter_shell"] is False
    assert any(item["label"] == "Übersicht" for item in model["navigation"])


def test_gui_shell_summary_mentions_qt() -> None:
    summary = summarize_gui_shell_model(build_gui_shell_model())
    assert "Modern Qt shell: True" in summary
