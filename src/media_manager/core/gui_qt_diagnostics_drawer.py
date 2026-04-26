from __future__ import annotations

from collections.abc import Mapping
from typing import Any

DIAGNOSTICS_DRAWER_SCHEMA_VERSION = "1.0"


def build_qt_diagnostics_drawer(diagnostics: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    items = [dict(item) for item in diagnostics or []]
    errors = [item for item in items if item.get("level") == "error" or item.get("severity") == "error"]
    warnings = [item for item in items if item.get("level") == "warning" or item.get("severity") == "warning"]
    infos = [item for item in items if item not in errors and item not in warnings]
    ordered = [*errors, *warnings, *infos]
    return {"schema_version": DIAGNOSTICS_DRAWER_SCHEMA_VERSION, "diagnostic_count": len(items), "error_count": len(errors), "warning_count": len(warnings), "items": ordered, "status": "error" if errors else "warning" if warnings else "ok"}


__all__ = ["DIAGNOSTICS_DRAWER_SCHEMA_VERSION", "build_qt_diagnostics_drawer"]
