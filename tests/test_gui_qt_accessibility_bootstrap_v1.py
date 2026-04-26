from media_manager.core.gui_qt_accessibility_adapter import build_accessibility_labels, find_missing_accessibility_labels
from media_manager.core.gui_qt_bootstrap_plan import build_qt_bootstrap_plan
from media_manager.core.gui_qt_manual_smoke_checklist import build_qt_manual_smoke_checklist, mark_smoke_check_done
from media_manager.core.gui_qt_renderer_blueprint import build_qt_renderer_blueprint

def test_accessibility_labels_are_generated_from_blueprint() -> None:
    blueprint = build_qt_renderer_blueprint({
        "navigation": [{"id": "dashboard", "label": "Dashboard"}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard"},
    })
    labels = build_accessibility_labels(blueprint)
    assert labels["label_count"] > 0
    assert find_missing_accessibility_labels(labels)["valid"] is True

def test_manual_smoke_checklist_can_be_marked_done() -> None:
    checklist = build_qt_manual_smoke_checklist(language="de", has_people_bundle=False)
    updated = mark_smoke_check_done(checklist, "launch")
    assert updated["done_count"] == 1

def test_bootstrap_plan_is_ready_and_non_executing() -> None:
    model = {
        "language": "en",
        "theme": {"theme": "modern-dark", "tokens": {"background": "#000", "surface": "#111", "text": "#fff", "accent": "#0af"}},
        "settings": {"language": "en"},
        "home_state": {},
        "navigation": [{"id": "dashboard", "label": "Dashboard", "active": True}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": []},
    }
    plan = build_qt_bootstrap_plan(model)
    assert plan["kind"] == "qt_bootstrap_plan"
    assert plan["ready_for_qt_runtime"] is True
    assert plan["diagnostics"]["signal_map"]["valid"] is True
