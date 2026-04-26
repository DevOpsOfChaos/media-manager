from media_manager.core.gui_qt_demo_workspace import build_demo_shell_model
from media_manager.core.gui_qt_navigation_shell_plan import build_navigation_shell_plan, summarize_navigation_shell_plan
from media_manager.core.gui_qt_view_templates import build_view_template_catalog, normalize_template_id


def test_template_catalog_and_navigation_shell() -> None:
    catalog = build_view_template_catalog()
    assert catalog["template_count"] >= 5
    assert normalize_template_id("runs") == "run-history"

    plan = build_navigation_shell_plan(build_demo_shell_model())
    summary = summarize_navigation_shell_plan(plan)
    assert summary["has_active"] is True
    assert summary["enabled_count"] >= 2
