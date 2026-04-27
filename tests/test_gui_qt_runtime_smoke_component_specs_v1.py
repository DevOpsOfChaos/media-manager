from media_manager.core.gui_qt_runtime_smoke_component_specs import build_qt_runtime_smoke_component_specs, lookup_qt_runtime_smoke_component


def test_component_specs_include_required_runtime_smoke_components() -> None:
    specs = build_qt_runtime_smoke_component_specs()
    assert specs["summary"]["component_count"] >= 6
    assert specs["components"]["StatusBanner"]["qt_widget"] == "QFrame"
    assert specs["components"]["DataTable"]["role"] == "table"
    assert specs["capabilities"]["requires_pyside6"] is False


def test_component_lookup_returns_safe_fallback_for_unknown_component() -> None:
    spec = lookup_qt_runtime_smoke_component("UnknownThing")
    assert spec["supported"] is False
    assert spec["qt_widget"] == "QWidget"
    assert spec["layout"] == "QVBoxLayout"
