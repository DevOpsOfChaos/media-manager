from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_command_center import build_command_center
from .gui_qt_demo_workspace import build_demo_shell_model
from .gui_qt_inspector_panel import build_inspector_panel
from .gui_qt_page_chrome import build_page_chrome
from .gui_qt_release_smoke_pack import build_release_smoke_pack
from .gui_qt_settings_workspace import build_settings_workspace
from .gui_qt_view_templates import get_view_template, validate_page_against_template
from .gui_qt_visual_density_tuner import build_density_tuning

PRODUCT_SURFACE_SCHEMA_VERSION = "1.0"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_product_surface(shell_model: Mapping[str, Any] | None = None, *, language: str = "en", density: str = "comfortable") -> dict[str, object]:
    shell = dict(shell_model or build_demo_shell_model())
    page = _mapping(shell.get("page"))
    page_id = str(page.get("page_id") or shell.get("active_page_id") or "dashboard")
    surface = {
        "schema_version": PRODUCT_SURFACE_SCHEMA_VERSION,
        "kind": "qt_product_surface",
        "page_id": page_id,
        "language": language,
        "chrome": build_page_chrome(page, language=language),
        "template": get_view_template(page_id),
        "template_validation": validate_page_against_template(page),
        "density": build_density_tuning(density, page_id=page_id),
        "command_center": build_command_center(query=""),
        "settings_workspace": build_settings_workspace({"language": language, "density": density}),
        "inspector": build_inspector_panel(shell, title="Shell model inspector"),
        "smoke_pack": build_release_smoke_pack(shell_model=shell, language=language),
        "executes_commands": False,
    }
    surface["summary"] = {
        "page_id": page_id,
        "template_valid": surface["template_validation"]["valid"],
        "command_count": surface["command_center"]["row_count"],
        "smoke_scenarios": surface["smoke_pack"]["scenario_count"],
    }
    return surface


def validate_product_surface(surface: Mapping[str, Any]) -> dict[str, object]:
    problems = []
    if surface.get("executes_commands") is not False:
        problems.append("surface_may_execute_commands")
    if not surface.get("chrome"):
        problems.append("missing_chrome")
    if not surface.get("template"):
        problems.append("missing_template")
    if not surface.get("command_center"):
        problems.append("missing_command_center")
    return {
        "schema_version": PRODUCT_SURFACE_SCHEMA_VERSION,
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "page_id": surface.get("page_id"),
    }


__all__ = ["PRODUCT_SURFACE_SCHEMA_VERSION", "build_product_surface", "validate_product_surface"]
