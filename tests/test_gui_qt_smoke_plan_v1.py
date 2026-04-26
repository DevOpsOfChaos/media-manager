from media_manager.core.gui_qt_smoke_plan import build_qt_smoke_plan, summarize_qt_smoke_plan


def test_qt_smoke_plan_passes_for_minimal_shell_model():
    shell = {
        "active_page_id": "dashboard",
        "window": {"width": 1400, "height": 900},
        "page": {"page_id": "dashboard", "title": "Dashboard"},
        "navigation": [{"id": "dashboard", "label": "Dashboard"}],
    }
    plan = build_qt_smoke_plan(shell)
    assert plan["ok"] is True
    assert "4/4" in summarize_qt_smoke_plan(plan)
