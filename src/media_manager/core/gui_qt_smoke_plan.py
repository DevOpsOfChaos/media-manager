from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_page_controller import build_page_controller_state, plan_page_switch
from .gui_qt_window_state import build_qt_window_state

SMOKE_PLAN_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _build_desktop_plan(shell_model: Mapping[str, Any]) -> Mapping[str, Any]:
    try:
        from .gui_qt_desktop_plan import build_qt_desktop_plan

        return build_qt_desktop_plan(shell_model)
    except Exception:
        return {"page_plan": shell_model.get("page"), "summary": {"fallback": True}}


def build_qt_smoke_plan(shell_model: Mapping[str, Any]) -> dict[str, Any]:
    desktop_plan = _build_desktop_plan(shell_model)
    controller = build_page_controller_state(shell_model)
    window_state = build_qt_window_state(shell_model)
    checks = [
        {"id": "desktop_plan", "ok": bool(desktop_plan.get("page_plan"))},
        {"id": "navigation", "ok": bool(controller.get("known_page_ids"))},
        {"id": "window_state", "ok": int(window_state.get("width", 0)) > 0 and int(window_state.get("height", 0)) > 0},
    ]
    known = controller.get("known_page_ids") if isinstance(controller.get("known_page_ids"), list) else []
    first_page = known[0] if known else controller.get("active_page_id")
    switch = plan_page_switch(controller, str(first_page))
    checks.append({"id": "page_switch", "ok": bool(switch.get("allowed"))})
    return {
        "schema_version": SMOKE_PLAN_SCHEMA_VERSION,
        "kind": "qt_smoke_plan",
        "checks": checks,
        "ok": all(bool(item.get("ok")) for item in checks),
        "desktop_plan_summary": _as_mapping(desktop_plan.get("summary")),
        "window_state": window_state,
        "controller": controller,
    }


def summarize_qt_smoke_plan(smoke_plan: Mapping[str, Any]) -> str:
    checks = smoke_plan.get("checks") if isinstance(smoke_plan.get("checks"), list) else []
    passed = sum(1 for item in checks if isinstance(item, Mapping) and item.get("ok"))
    return f"Qt smoke plan: {passed}/{len(checks)} checks passed"


__all__ = ["SMOKE_PLAN_SCHEMA_VERSION", "build_qt_smoke_plan", "summarize_qt_smoke_plan"]
