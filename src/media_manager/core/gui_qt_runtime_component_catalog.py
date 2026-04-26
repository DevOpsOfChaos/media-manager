from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_COMPONENT_CATALOG_SCHEMA_VERSION = "1.0"

_COMPONENTS: dict[str, dict[str, object]] = {
    "ShellFrame": {"qt_widget": "QWidget", "layout": "QHBoxLayout", "role": "application_shell"},
    "NavigationRail": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "navigation"},
    "NavigationItem": {"qt_widget": "QPushButton", "layout": None, "role": "navigation_item"},
    "StatusBar": {"qt_widget": "QStatusBar", "layout": None, "role": "status"},
    "DashboardPage": {"qt_widget": "QWidget", "layout": "QVBoxLayout", "role": "page"},
    "HeroSection": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "dashboard_section"},
    "ActivitySection": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "dashboard_section"},
    "CardGridSection": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "dashboard_section"},
    "Section": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "section"},
    "EmptyStateSection": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "empty_state"},
    "MetricStrip": {"qt_widget": "QFrame", "layout": "QHBoxLayout", "role": "dashboard_metric_strip"},
    "Metric": {"qt_widget": "QLabel", "layout": None, "role": "dashboard_metric"},
    "DashboardItem": {"qt_widget": "QLabel", "layout": None, "role": "dashboard_item"},
    "CardGrid": {"qt_widget": "QWidget", "layout": "QGridLayout", "role": "dashboard_card_grid"},
    "Card": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "dashboard_card"},
    "PeopleReviewPage": {"qt_widget": "QWidget", "layout": "QHBoxLayout", "role": "page"},
    "PeopleGroupLane": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "people_review_section"},
    "FaceGallery": {"qt_widget": "QScrollArea", "layout": "QGridLayout", "role": "people_review_section"},
    "PeopleReviewSection": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "people_review_section"},
    "PeopleGroupButton": {"qt_widget": "QPushButton", "layout": None, "role": "people_group"},
    "FaceCard": {"qt_widget": "QFrame", "layout": "QVBoxLayout", "role": "people_face"},
    "PeopleReviewItem": {"qt_widget": "QLabel", "layout": None, "role": "people_review_item"},
    "Text": {"qt_widget": "QLabel", "layout": None, "role": "text"},
    "GenericPage": {"qt_widget": "QWidget", "layout": "QVBoxLayout", "role": "page"},
    "Container": {"qt_widget": "QWidget", "layout": "QVBoxLayout", "role": "container"},
}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_component_catalog() -> dict[str, object]:
    """Return the declarative component-to-Qt mapping used by desktop integration.

    The catalog is data-only. It intentionally contains Qt class names as
    strings, not imported PySide6 objects, so tests remain headless.
    """

    return {
        "schema_version": QT_RUNTIME_COMPONENT_CATALOG_SCHEMA_VERSION,
        "kind": "qt_runtime_component_catalog",
        "components": {key: dict(value) for key, value in sorted(_COMPONENTS.items())},
        "component_count": len(_COMPONENTS),
        "requires_pyside6": False,
    }


def lookup_qt_component_spec(component: str | None, catalog: Mapping[str, Any] | None = None) -> dict[str, object]:
    payload = _mapping(catalog or build_qt_runtime_component_catalog())
    components = _mapping(payload.get("components"))
    name = _text(component, "Container")
    spec = _mapping(components.get(name))
    if spec:
        return {"component": name, "supported": True, **dict(spec)}
    return {
        "component": name,
        "supported": False,
        "qt_widget": "QWidget",
        "layout": "QVBoxLayout",
        "role": "unsupported_component",
    }


def component_catalog_summary(catalog: Mapping[str, Any]) -> dict[str, object]:
    components = _mapping(catalog.get("components"))
    supported_widgets = sorted({str(_mapping(spec).get("qt_widget")) for spec in components.values() if isinstance(spec, Mapping)})
    return {
        "schema_version": QT_RUNTIME_COMPONENT_CATALOG_SCHEMA_VERSION,
        "component_count": len(components),
        "qt_widget_count": len(supported_widgets),
        "qt_widgets": supported_widgets,
        "requires_pyside6": bool(catalog.get("requires_pyside6")),
    }


__all__ = [
    "QT_RUNTIME_COMPONENT_CATALOG_SCHEMA_VERSION",
    "build_qt_runtime_component_catalog",
    "component_catalog_summary",
    "lookup_qt_component_spec",
]
