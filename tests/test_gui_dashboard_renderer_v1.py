from media_manager.core.gui_dashboard_renderer import build_dashboard_render_spec


def test_dashboard_renderer_contains_hero_and_cards() -> None:
    spec = build_dashboard_render_spec({
        "page_id": "dashboard",
        "title": "Dashboard",
        "hero": {"title": "Welcome"},
        "cards": [{"id": "runs", "title": "Runs", "metrics": {"count": 2}}],
    })

    assert spec["kind"] == "dashboard_render_spec"
    assert spec["summary"]["type_summary"]["hero"] == 1
    assert spec["summary"]["type_summary"]["card"] == 1
