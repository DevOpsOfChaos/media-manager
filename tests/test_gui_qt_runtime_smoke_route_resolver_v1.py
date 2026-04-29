from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_qt_runtime_smoke_route_resolver import resolve_qt_runtime_smoke_route
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_route_resolver_maps_runtime_smoke_to_page_and_visible_surface() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    route = resolve_qt_runtime_smoke_route(bundle)

    assert route["resolved"] is True
    assert route["page_id"] == "runtime-smoke"
    assert route["page_model_kind"] == "qt_runtime_smoke_page_model"
    assert route["visible_surface_kind"] == "qt_runtime_smoke_visible_surface"
    assert route["summary"]["opens_window"] is False


def test_guarded_bundle_contains_ready_route_resolution() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())

    assert bundle["route_resolution"]["ready"] is True
    assert bundle["summary"]["route_resolved"] is True
