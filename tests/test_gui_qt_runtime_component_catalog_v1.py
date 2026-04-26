from __future__ import annotations

from media_manager.core.gui_qt_runtime_component_catalog import (
    build_qt_runtime_component_catalog,
    component_catalog_summary,
    lookup_qt_component_spec,
)


def test_runtime_component_catalog_maps_core_shell_and_people_components() -> None:
    catalog = build_qt_runtime_component_catalog()

    assert catalog["requires_pyside6"] is False
    assert lookup_qt_component_spec("ShellFrame", catalog)["qt_widget"] == "QWidget"
    assert lookup_qt_component_spec("NavigationItem", catalog)["qt_widget"] == "QPushButton"
    assert lookup_qt_component_spec("PeopleReviewPage", catalog)["layout"] == "QHBoxLayout"
    assert lookup_qt_component_spec("FaceCard", catalog)["qt_widget"] == "QFrame"


def test_runtime_component_catalog_uses_safe_fallback_for_unknown_components() -> None:
    spec = lookup_qt_component_spec("UnknownFancyWidget")

    assert spec["supported"] is False
    assert spec["qt_widget"] == "QWidget"
    assert spec["layout"] == "QVBoxLayout"


def test_runtime_component_catalog_summary_is_headless() -> None:
    summary = component_catalog_summary(build_qt_runtime_component_catalog())

    assert summary["component_count"] >= 20
    assert "QWidget" in summary["qt_widgets"]
    assert summary["requires_pyside6"] is False
