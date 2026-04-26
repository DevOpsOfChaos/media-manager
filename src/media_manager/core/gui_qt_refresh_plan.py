from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REFRESH_PLAN_SCHEMA_VERSION = "1.0"


def _map(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _value(payload: Mapping[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        current = _map(current).get(part)
    return current


def _step(step_id: str, reason: str, *, scope: str, priority: int) -> dict[str, object]:
    return {"id": step_id, "reason": reason, "scope": scope, "priority": priority}


def build_qt_refresh_plan(
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
) -> dict[str, object]:
    """Build a conservative visible-UI refresh plan from two shell/page states."""
    before = _map(before)
    after = _map(after)
    steps: list[dict[str, object]] = []

    checks = [
        ("theme.theme", "rebuild_stylesheet", "theme changed", "application", 10),
        ("language", "refresh_text", "language changed", "application", 20),
        ("active_page_id", "rebuild_page", "active page changed", "page", 30),
        ("page.schema_version", "rebuild_page", "page schema changed", "page", 40),
        ("status_bar.text", "refresh_status_bar", "status text changed", "status", 60),
        ("navigation", "refresh_navigation", "navigation changed", "navigation", 50),
    ]
    seen: set[str] = set()
    for dotted, step_id, reason, scope, priority in checks:
        if _value(before, dotted) != _value(after, dotted) and step_id not in seen:
            steps.append(_step(step_id, reason, scope=scope, priority=priority))
            seen.add(step_id)

    if not before and after and "bootstrap_window" not in seen:
        steps.insert(0, _step("bootstrap_window", "initial model", scope="window", priority=0))

    ordered = sorted(steps, key=lambda item: int(item["priority"]))
    return {
        "schema_version": REFRESH_PLAN_SCHEMA_VERSION,
        "kind": "qt_refresh_plan",
        "step_count": len(ordered),
        "requires_full_rebuild": any(step["id"] in {"bootstrap_window", "rebuild_stylesheet"} for step in ordered),
        "requires_page_rebuild": any(step["id"] == "rebuild_page" for step in ordered),
        "steps": ordered,
    }


__all__ = ["REFRESH_PLAN_SCHEMA_VERSION", "build_qt_refresh_plan"]
