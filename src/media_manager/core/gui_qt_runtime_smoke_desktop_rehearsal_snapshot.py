from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_qt_runtime_smoke_desktop_rehearsal_snapshot(report: Mapping[str, Any]) -> dict[str, object]:
    payload = {
        "kind": report.get("kind"),
        "ready": report.get("ready"),
        "decision": report.get("decision"),
        "summary": _mapping(report.get("summary")),
    }
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_rehearsal_snapshot",
        "payload_hash": _hash(payload),
        "payload": payload,
        "summary": {
            "ready": bool(report.get("ready")),
            "decision": report.get("decision"),
            "local_only": _mapping(report.get("summary")).get("local_only", True),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_rehearsal_snapshot"]
