from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .gui_review_workbench_stateful_rebuild import (
    build_review_workbench_stateful_rebuild_bundle,
    normalize_review_workbench_rebuild_intent,
)

REVIEW_WORKBENCH_STATEFUL_CALLBACK_SCHEMA_VERSION = "1.0"
REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND = "ui_review_workbench_stateful_callback_plan"
REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND = "ui_review_workbench_stateful_callback_response"

_INTENT_KIND_TO_ACTION = {
    "filter_query_changed": "set_query",
    "filter_status_changed": "set_filter",
    "sort_mode_changed": "set_sort",
    "lane_selected": "select_lane",
    "table_row_activated": "open_selected_lane",
    "toolbar_open_selected_lane": "open_selected_lane",
    "toolbar_reset_filters": "reset_view",
    "toolbar_refresh": "refresh_view",
    "toolbar_apply_reviewed_decisions": "disabled_apply",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback


def map_review_workbench_callback_intent_to_rebuild_intent(intent: Mapping[str, Any]) -> dict[str, object]:
    """Convert a Qt callback/interaction intent into the reducer intent used by the rebuild loop."""

    raw = _as_mapping(intent)
    intent_kind = _text(raw.get("intent_kind"))
    action = _text(raw.get("action")) or _INTENT_KIND_TO_ACTION.get(intent_kind, "refresh_view")
    return normalize_review_workbench_rebuild_intent(
        action=action,
        lane_id=raw.get("lane_id"),
        status=raw.get("status"),
        query=raw.get("query"),
        sort_mode=raw.get("sort_mode"),
        page=raw.get("page"),
        page_size=raw.get("page_size"),
    )


def _callback_rows(service_bundle: Mapping[str, Any]) -> list[dict[str, object]]:
    plan = _as_mapping(service_bundle.get("callback_mount_plan"))
    rows: list[dict[str, object]] = []
    for raw_mount in _as_list(plan.get("callback_mounts")):
        mount = _as_mapping(raw_mount)
        intent_kind = _text(mount.get("intent_kind"))
        action = _INTENT_KIND_TO_ACTION.get(intent_kind, "refresh_view")
        stateful = action in {"set_query", "set_filter", "set_sort", "select_lane", "reset_view", "refresh_view"}
        rows.append(
            {
                "mount_id": mount.get("mount_id"),
                "object_name": mount.get("object_name"),
                "qt_signal": mount.get("qt_signal"),
                "intent_kind": intent_kind,
                "rebuild_action": action,
                "rebuilds_page_state": stateful,
                "route_only": action == "open_selected_lane",
                "disabled_apply": action == "disabled_apply",
                "enabled": bool(mount.get("enabled")),
                "executes_commands": False,
                "executes_media_operations": False,
            }
        )
    return rows


def build_review_workbench_stateful_callback_plan(service_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Describe how mounted Qt callbacks may request a non-executing page-state rebuild."""

    callback_plan = _as_mapping(service_bundle.get("callback_mount_plan"))
    rebuild_loop = _as_mapping(service_bundle.get("stateful_rebuild_loop"))
    rows = _callback_rows(service_bundle)
    enabled_rows = [row for row in rows if row.get("enabled") is True]
    rebuild_rows = [row for row in rows if row.get("rebuilds_page_state") is True]
    checks = [
        {
            "id": "callback-mount-plan-ready",
            "label": "Callback mounts are available before connecting stateful rebuilds",
            "ok": bool(_as_mapping(callback_plan.get("readiness")).get("ready")),
        },
        {
            "id": "stateful-rebuild-loop-ready",
            "label": "Stateful rebuild loop is ready before callbacks request page replacement",
            "ok": bool(_as_mapping(rebuild_loop.get("readiness")).get("ready")),
        },
        {
            "id": "rebuild-callbacks-present",
            "label": "Filter, sort, selection, reset and refresh callbacks can produce rebuild requests",
            "ok": {"set_query", "set_filter", "set_sort", "select_lane", "reset_view", "refresh_view"}.issubset(
                {str(row.get("rebuild_action")) for row in rows}
            ),
        },
        {
            "id": "non-executing-callbacks",
            "label": "Stateful callback bridge never executes commands or media operations",
            "ok": all(row.get("executes_commands") is False and row.get("executes_media_operations") is False for row in rows),
        },
    ]
    failed = [check for check in checks if check.get("ok") is not True]
    return {
        "schema_version": REVIEW_WORKBENCH_STATEFUL_CALLBACK_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND,
        "page_id": "review-workbench",
        "generated_at_utc": _now_utc(),
        "callback_rebuild_bindings": rows,
        "response_contract": {
            "callback_intent": "original non-executing UI intent emitted by the Qt callback",
            "normalized_rebuild_intent": "ui_review_workbench_update_intent consumed by the reducer",
            "rebuild_bundle": "ui_review_workbench_stateful_rebuild_bundle with next_page_state",
            "render_update_strategy": "replace_review_workbench_page_state",
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "writes_app_state": False,
            "rebuilds_view_state": True,
            "apply_enabled": False,
        },
        "readiness": {
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
            "failed_check_count": len(failed),
            "checks": checks,
            "next_action": (
                "Pass stateful_rebuild_handler to the lazy Qt builder so callbacks can request next_page_state bundles."
                if not failed
                else "Fix callback or rebuild-loop readiness before wiring stateful Qt callbacks."
            ),
        },
        "summary": {
            "callback_binding_count": len(rows),
            "enabled_callback_binding_count": len(enabled_rows),
            "page_rebuild_callback_count": len(rebuild_rows),
            "route_only_callback_count": sum(1 for row in rows if row.get("route_only") is True),
            "disabled_apply_callback_count": sum(1 for row in rows if row.get("disabled_apply") is True),
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
        },
    }


def build_review_workbench_stateful_callback_response(
    service_bundle: Mapping[str, Any],
    callback_intent: Mapping[str, Any],
    **rebuild_kwargs: Any,
) -> dict[str, object]:
    """Apply a callback intent through the stateful rebuild loop and return a GUI replacement payload."""

    normalized = map_review_workbench_callback_intent_to_rebuild_intent(callback_intent)
    rebuild = build_review_workbench_stateful_rebuild_bundle(service_bundle, normalized, **rebuild_kwargs)
    render_update = _as_mapping(rebuild.get("render_update"))
    checks = [
        {
            "id": "callback-intent-non-executing",
            "label": "Original callback intent does not execute commands",
            "ok": _as_mapping(callback_intent).get("executes_commands") is False,
        },
        {
            "id": "normalized-intent-non-executing",
            "label": "Normalized reducer intent does not execute commands",
            "ok": normalized.get("executes_commands") is False,
        },
        {
            "id": "rebuild-ready",
            "label": "Stateful rebuild returned a ready next page-state bundle",
            "ok": bool(_as_mapping(rebuild.get("readiness")).get("ready")),
        },
        {
            "id": "render-update-safe",
            "label": "Render update replaces local page state without opening windows or executing commands",
            "ok": render_update.get("executes_commands") is False and render_update.get("opens_window") is False,
        },
    ]
    failed = [check for check in checks if check.get("ok") is not True]
    return {
        "schema_version": REVIEW_WORKBENCH_STATEFUL_CALLBACK_SCHEMA_VERSION,
        "kind": REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND,
        "generated_at_utc": _now_utc(),
        "page_id": "review-workbench",
        "callback_intent": dict(callback_intent),
        "normalized_rebuild_intent": normalized,
        "rebuild_bundle": rebuild,
        "next_page_state": _as_mapping(rebuild.get("next_page_state")),
        "render_update": dict(render_update),
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "executes_media_operations": False,
            "writes_app_state": False,
            "apply_enabled": False,
        },
        "readiness": {
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
            "failed_check_count": len(failed),
            "checks": checks,
            "next_action": (
                "Replace the visible Review Workbench page with next_page_state and keep the desktop shell intact."
                if not failed
                else "Do not update the visible page until callback rebuild checks pass."
            ),
        },
        "summary": {
            "callback_intent_kind": _as_mapping(callback_intent).get("intent_kind"),
            "rebuild_action": normalized.get("action"),
            "changed": _as_mapping(rebuild.get("summary")).get("changed"),
            "selected_lane_id": _as_mapping(rebuild.get("summary")).get("selected_lane_id"),
            "table_row_count": _as_mapping(rebuild.get("summary")).get("table_row_count"),
            "ready": not failed,
            "status": "ready" if not failed else "blocked",
            "executes_commands": False,
        },
    }


def write_review_workbench_stateful_callback_plan(out_dir: str | Path, service_bundle: Mapping[str, Any]) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    plan = build_review_workbench_stateful_callback_plan(service_bundle)
    files: list[tuple[str, Mapping[str, Any]]] = [
        ("review_workbench_stateful_callback_plan.json", plan),
        (
            "review_workbench_stateful_callback_bindings.json",
            {
                "kind": "ui_review_workbench_stateful_callback_bindings",
                "page_id": "review-workbench",
                "callback_rebuild_bindings": plan.get("callback_rebuild_bindings", []),
                "executes_commands": False,
            },
        ),
    ]
    written_files: list[str] = []
    for filename, payload in files:
        path = root / filename
        path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written_files.append(str(path))
    readme = root / "README.txt"
    readme.write_text(
        "Review Workbench stateful callback plan\n"
        "Maps lazy Qt callbacks to non-executing stateful page rebuild requests.\n"
        "This contract does not import PySide6, open windows, write app state, execute commands, or perform media operations.\n",
        encoding="utf-8",
    )
    written_files.append(str(readme))
    return {**plan, "output_dir": str(root), "written_files": written_files, "written_file_count": len(written_files)}


__all__ = [
    "REVIEW_WORKBENCH_STATEFUL_CALLBACK_PLAN_KIND",
    "REVIEW_WORKBENCH_STATEFUL_CALLBACK_RESPONSE_KIND",
    "REVIEW_WORKBENCH_STATEFUL_CALLBACK_SCHEMA_VERSION",
    "build_review_workbench_stateful_callback_plan",
    "build_review_workbench_stateful_callback_response",
    "map_review_workbench_callback_intent_to_rebuild_intent",
    "write_review_workbench_stateful_callback_plan",
]
