from __future__ import annotations

from collections.abc import Mapping

from .gui_qt_runtime_smoke_adapter_snapshot import build_qt_runtime_smoke_adapter_snapshot
from .gui_qt_runtime_smoke_adapter_validation import validate_qt_runtime_smoke_adapter_bundle
from .gui_qt_runtime_smoke_event_map import build_qt_runtime_smoke_event_map
from .gui_qt_runtime_smoke_interactions import build_qt_runtime_smoke_interaction_plan
from .gui_qt_runtime_smoke_render_plan import build_qt_runtime_smoke_render_plan
from .gui_qt_runtime_smoke_widget_tree import build_qt_runtime_smoke_widget_tree

QT_RUNTIME_SMOKE_ADAPTER_BUNDLE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_adapter_bundle(visible_surface: Mapping[str, object]) -> dict[str, object]:
    widget_tree = build_qt_runtime_smoke_widget_tree(visible_surface)
    render_plan = build_qt_runtime_smoke_render_plan(widget_tree, visible_surface.get("layout_plan") if isinstance(visible_surface.get("layout_plan"), Mapping) else None)
    interaction_plan = build_qt_runtime_smoke_interaction_plan(visible_surface)
    event_map = build_qt_runtime_smoke_event_map(interaction_plan)
    bundle: dict[str, object] = {
        "schema_version": QT_RUNTIME_SMOKE_ADAPTER_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_adapter_bundle",
        "page_id": visible_surface.get("page_id"),
        "visible_surface": dict(visible_surface),
        "widget_tree": widget_tree,
        "render_plan": render_plan,
        "interaction_plan": interaction_plan,
        "event_map": event_map,
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }
    validation = validate_qt_runtime_smoke_adapter_bundle(bundle)
    bundle["validation"] = validation
    bundle["ready_for_qt_runtime"] = bool(validation.get("valid"))
    bundle["snapshot"] = build_qt_runtime_smoke_adapter_snapshot(bundle)
    bundle["summary"] = {
        "ready_for_qt_runtime": bool(bundle["ready_for_qt_runtime"]),
        "render_step_count": validation["summary"]["render_step_count"],
        "binding_count": validation["summary"]["binding_count"],
        "event_count": validation["summary"]["event_count"],
        "problem_count": validation["problem_count"],
        "local_only": validation["summary"]["local_only"],
    }
    return bundle


__all__ = ["QT_RUNTIME_SMOKE_ADAPTER_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_adapter_bundle"]
