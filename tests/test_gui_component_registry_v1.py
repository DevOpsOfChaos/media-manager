from media_manager.core.gui_component_registry import build_component_registry, lookup_component, validate_widget_types
from media_manager.core.gui_widget_specs import build_widget_spec


def test_component_registry_validates_widget_tree() -> None:
    registry = build_component_registry()
    assert lookup_component(registry, "card")["available"] is True

    valid = validate_widget_types(registry, build_widget_spec("x", "card"))
    assert valid["valid"] is True

    invalid = validate_widget_types(registry, {"widget_type": "unknown-widget"})
    assert invalid["valid"] is False
    assert invalid["missing_widget_types"] == ["unknown-widget"]
