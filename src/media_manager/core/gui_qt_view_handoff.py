from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from .gui_qt_app_frame_model import build_app_frame_model, summarize_app_frame

VIEW_HANDOFF_SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_view_handoff(shell_model: Mapping[str, Any], *, collapsed_navigation: bool = False) -> dict[str, object]:
    frame = build_app_frame_model(shell_model, collapsed_navigation=collapsed_navigation)
    page = _as_mapping(shell_model.get("page"))
    return {
        "schema_version": VIEW_HANDOFF_SCHEMA_VERSION,
        "kind": "qt_view_handoff",
        "generated_at_utc": _now(),
        "active_page_id": shell_model.get("active_page_id") or page.get("page_id"),
        "language": shell_model.get("language"),
        "theme": _as_mapping(shell_model.get("theme")).get("theme"),
        "frame": frame,
        "summary": summarize_app_frame(frame),
        "handoff_contract": {
            "consumer": "gui_desktop_qt",
            "executes_commands": False,
            "sensitive_people_assets_must_remain_local": True,
        },
    }


def validate_qt_view_handoff(payload: Mapping[str, Any]) -> dict[str, object]:
    problems: list[str] = []
    if payload.get("kind") != "qt_view_handoff":
        problems.append("kind must be qt_view_handoff")
    frame = _as_mapping(payload.get("frame"))
    if not frame:
        problems.append("frame is required")
    if not _as_mapping(frame.get("navigation_rail")):
        problems.append("navigation_rail is required")
    if not _as_mapping(frame.get("page_slots")):
        problems.append("page_slots is required")
    return {"valid": not problems, "problems": problems, "problem_count": len(problems)}


__all__ = ["VIEW_HANDOFF_SCHEMA_VERSION", "build_qt_view_handoff", "validate_qt_view_handoff"]
