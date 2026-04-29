from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_GUARDED_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_guarded_snapshot(guarded_integration: Mapping[str, Any]) -> dict[str, object]:
    """Create a stable snapshot for the whole guarded Runtime Smoke integration."""

    summary = dict(_mapping(guarded_integration.get("summary")))
    compact = {
        "kind": guarded_integration.get("kind"),
        "page_id": guarded_integration.get("page_id"),
        "summary": summary,
        "route": _mapping(_mapping(guarded_integration.get("page_handoff")).get("route")),
        "manual_readiness": _mapping(guarded_integration.get("manual_readiness")).get("summary"),
    }
    payload = json.dumps(compact, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_GUARDED_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_guarded_snapshot",
        "page_id": guarded_integration.get("page_id") or "runtime-smoke",
        "payload_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "payload": compact,
        "summary": summary,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_GUARDED_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_guarded_snapshot"]
