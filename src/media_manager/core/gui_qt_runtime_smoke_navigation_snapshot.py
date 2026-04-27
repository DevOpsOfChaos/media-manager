from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_NAVIGATION_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _stable_hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_qt_runtime_smoke_navigation_snapshot(page_handoff: Mapping[str, Any]) -> dict[str, object]:
    registry = _mapping(page_handoff.get("page_registry"))
    diagnostics = _mapping(page_handoff.get("diagnostics"))
    payload = {
        "kind": page_handoff.get("kind"),
        "route": _mapping(page_handoff.get("route")),
        "navigation_item": _mapping(page_handoff.get("navigation_item")),
        "registry_summary": _mapping(registry.get("summary")),
        "diagnostics_summary": _mapping(diagnostics.get("summary")),
    }
    return {
        "schema_version": QT_RUNTIME_SMOKE_NAVIGATION_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_navigation_snapshot",
        "payload_hash": _stable_hash(payload),
        "payload": payload,
        "summary": {
            "ready_for_shell_registration": bool(page_handoff.get("ready_for_shell_registration")),
            "page_count": _mapping(page_handoff.get("summary")).get("page_count", 0),
            "problem_count": _mapping(page_handoff.get("summary")).get("problem_count", 0),
            "local_only": _mapping(page_handoff.get("summary")).get("local_only", True),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_NAVIGATION_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_navigation_snapshot"]
