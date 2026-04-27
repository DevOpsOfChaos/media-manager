from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_ROUTE_VALIDATOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def validate_qt_runtime_smoke_route(route_model: Mapping[str, Any], navigation_item: Mapping[str, Any]) -> dict[str, object]:
    """Validate route/navigation safety before any visible Qt integration."""

    problems: list[dict[str, object]] = []
    guards = _mapping(route_model.get("guards"))
    security = _mapping(navigation_item.get("security"))
    if route_model.get("page_id") != navigation_item.get("page_id"):
        problems.append({"code": "page_id_mismatch"})
    if guards.get("local_only") is not True or security.get("local_only") is not True:
        problems.append({"code": "route_not_local_only"})
    if guards.get("opens_window") is not False or security.get("opens_window") is not False:
        problems.append({"code": "route_opens_window"})
    if guards.get("executes_commands") is not False or security.get("executes_commands") is not False:
        problems.append({"code": "route_executes_commands"})
    if guards.get("validation_valid") is not True and route_model.get("enabled") is True:
        problems.append({"code": "enabled_route_without_valid_adapter"})
    return {
        "schema_version": QT_RUNTIME_SMOKE_ROUTE_VALIDATOR_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_route_validation",
        "valid": not problems,
        "problem_count": len(problems),
        "problems": problems,
        "summary": {
            "route_id": route_model.get("route_id"),
            "page_id": route_model.get("page_id"),
            "navigation_enabled": bool(navigation_item.get("enabled")),
            "local_only": guards.get("local_only") is True and security.get("local_only") is True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_ROUTE_VALIDATOR_SCHEMA_VERSION", "validate_qt_runtime_smoke_route"]
