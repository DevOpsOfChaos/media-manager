from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

RELEASE_GATE_SCHEMA_VERSION = "1.0"


def build_release_gate(checks: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    items = []
    for raw in checks:
        status = str(raw.get("status") or ("passed" if raw.get("passed") else "failed"))
        severity = str(raw.get("severity") or ("error" if status in {"failed", "blocked"} else "info"))
        items.append({"id": str(raw.get("id") or raw.get("name") or "check"), "status": status, "severity": severity, "message": str(raw.get("message") or "")})
    error_count = sum(1 for item in items if item["severity"] == "error" or item["status"] in {"failed", "blocked"})
    warning_count = sum(1 for item in items if item["severity"] == "warning")
    return {
        "schema_version": RELEASE_GATE_SCHEMA_VERSION,
        "kind": "qt_release_gate",
        "check_count": len(items),
        "error_count": error_count,
        "warning_count": warning_count,
        "ready": error_count == 0,
        "checks": items,
    }


__all__ = ["RELEASE_GATE_SCHEMA_VERSION", "build_release_gate"]
