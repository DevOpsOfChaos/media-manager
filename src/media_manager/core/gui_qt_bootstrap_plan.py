from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_accessibility_adapter import build_accessibility_labels, find_missing_accessibility_labels
from .gui_qt_incremental_update import build_incremental_update_plan
from .gui_qt_lifecycle_model import build_qt_lifecycle_plan
from .gui_qt_manual_smoke_checklist import build_qt_manual_smoke_checklist
from .gui_qt_renderer_blueprint import build_qt_renderer_blueprint
from .gui_qt_signal_map import build_qt_signal_map, validate_signal_map
from .gui_qt_theme_adapter import build_qt_theme_adapter_payload, validate_qt_theme_adapter

BOOTSTRAP_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_qt_bootstrap_plan(shell_model: Mapping[str, Any], *, previous_model: Mapping[str, Any] | None = None) -> dict[str, object]:
    blueprint = build_qt_renderer_blueprint(shell_model)
    signal_map = build_qt_signal_map(blueprint)
    theme_adapter = build_qt_theme_adapter_payload(_mapping(shell_model.get("theme")))
    accessibility = build_accessibility_labels(blueprint)
    lifecycle = build_qt_lifecycle_plan(
        has_settings=bool(shell_model.get("settings")),
        has_people_bundle=bool(_mapping(_mapping(shell_model.get("home_state")).get("people_review")).get("bundle_dir")),
        dry_run=True,
    )
    update_plan = build_incremental_update_plan(previous_model or {}, shell_model)
    signal_validation = validate_signal_map(signal_map)
    theme_validation = validate_qt_theme_adapter(theme_adapter)
    accessibility_validation = find_missing_accessibility_labels(accessibility)
    ready = bool(signal_validation["valid"] and theme_validation["valid"] and accessibility_validation["valid"])
    return {
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "kind": "qt_bootstrap_plan",
        "ready_for_qt_runtime": ready,
        "blueprint": blueprint,
        "signal_map": signal_map,
        "theme_adapter": theme_adapter,
        "accessibility": accessibility,
        "lifecycle": lifecycle,
        "update_plan": update_plan,
        "manual_smoke_checklist": build_qt_manual_smoke_checklist(
            language=str(shell_model.get("language") or "en"),
            has_people_bundle=bool(_mapping(_mapping(shell_model.get("home_state")).get("people_review")).get("bundle_dir")),
        ),
        "diagnostics": {
            "signal_map": signal_validation,
            "theme": theme_validation,
            "accessibility": accessibility_validation,
        },
    }

__all__ = ["BOOTSTRAP_SCHEMA_VERSION", "build_qt_bootstrap_plan"]
