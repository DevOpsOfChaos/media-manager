from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

SNAPSHOT_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_gui_workspace_snapshot(
    *,
    shell_model: Mapping[str, Any] | None = None,
    page_model: Mapping[str, Any] | None = None,
    selection_state: Mapping[str, Any] | None = None,
    audit_log: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    shell = _mapping(shell_model)
    page = _mapping(page_model or shell.get("page"))
    selection = _mapping(selection_state)
    audit = _mapping(audit_log)
    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "kind": "gui_workspace_snapshot",
        "created_at_utc": _now_utc(),
        "active_page_id": shell.get("active_page_id") or page.get("page_id"),
        "language": shell.get("language"),
        "theme": _mapping(shell.get("theme")).get("theme") if shell else None,
        "page": {
            "page_id": page.get("page_id"),
            "title": page.get("title"),
            "kind": page.get("kind"),
            "layout": page.get("layout"),
        },
        "selection": dict(selection),
        "audit_summary": {
            "event_count": audit.get("event_count", 0),
            "event_type_summary": audit.get("event_type_summary", {}),
        },
        "safe_to_restore": True,
    }


def summarize_workspace_snapshot(snapshot: Mapping[str, Any]) -> str:
    page = _mapping(snapshot.get("page"))
    return "\n".join(
        [
            "GUI workspace snapshot",
            f"  Page: {page.get('title') or snapshot.get('active_page_id')}",
            f"  Language: {snapshot.get('language') or '-'}",
            f"  Theme: {snapshot.get('theme') or '-'}",
            f"  Audit events: {_mapping(snapshot.get('audit_summary')).get('event_count', 0)}",
        ]
    )


def snapshot_is_compatible(snapshot: Mapping[str, Any]) -> bool:
    return snapshot.get("schema_version") == SNAPSHOT_SCHEMA_VERSION and snapshot.get("kind") == "gui_workspace_snapshot"


__all__ = [
    "SNAPSHOT_SCHEMA_VERSION",
    "build_gui_workspace_snapshot",
    "snapshot_is_compatible",
    "summarize_workspace_snapshot",
]
