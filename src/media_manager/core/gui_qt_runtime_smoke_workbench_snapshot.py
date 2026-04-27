from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_WORKBENCH_SNAPSHOT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _stable_hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_qt_runtime_smoke_workbench_snapshot(workbench: Mapping[str, Any]) -> dict[str, object]:
    summary = _mapping(workbench.get("summary"))
    payload = {
        "kind": workbench.get("kind"),
        "active_page_id": workbench.get("active_page_id"),
        "status": workbench.get("status"),
        "summary": dict(summary),
        "recommended_next_step": workbench.get("recommended_next_step"),
    }
    return {
        "schema_version": QT_RUNTIME_SMOKE_WORKBENCH_SNAPSHOT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_workbench_snapshot",
        "payload_hash": _stable_hash(payload),
        "payload": payload,
        "summary": {
            "section_count": summary.get("section_count", 0),
            "card_count": summary.get("card_count", 0),
            "ready_for_runtime_review": bool(summary.get("ready_for_runtime_review")),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_WORKBENCH_SNAPSHOT_SCHEMA_VERSION", "build_qt_runtime_smoke_workbench_snapshot"]
