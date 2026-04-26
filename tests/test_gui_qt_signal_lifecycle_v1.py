from media_manager.core.gui_qt_lifecycle_model import build_qt_lifecycle_plan, mark_lifecycle_stage
from media_manager.core.gui_qt_renderer_blueprint import build_qt_renderer_blueprint
from media_manager.core.gui_qt_signal_map import build_qt_signal_map, validate_signal_map

def test_signal_map_is_non_executing() -> None:
    blueprint = build_qt_renderer_blueprint({
        "navigation": [{"id": "people-review", "label": "People", "active": True}],
        "page": {"page_id": "people-review", "kind": "people_review_page", "title": "People", "groups": []},
    })
    signal_map = build_qt_signal_map(blueprint)
    assert signal_map["summary"]["binding_count"] >= 1
    assert validate_signal_map(signal_map)["valid"] is True
    assert all(binding["executes_immediately"] is False for binding in signal_map["bindings"])

def test_lifecycle_plan_can_mark_stage_done() -> None:
    plan = build_qt_lifecycle_plan(has_settings=True, has_people_bundle=True, dry_run=True)
    assert plan["summary"]["stage_count"] >= 6
    updated = mark_lifecycle_stage(plan, "bootstrap", "done")
    assert updated["summary"]["done_count"] == 1
