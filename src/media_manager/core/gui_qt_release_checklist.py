from __future__ import annotations

from collections.abc import Mapping
from typing import Any

RELEASE_CHECKLIST_SCHEMA_VERSION = "1.0"


def _item(item_id: str, title: str, *, required: bool = True, passed: bool = False, evidence: object = None) -> dict[str, object]:
    return {"id": item_id, "title": title, "required": required, "passed": bool(passed), "evidence": evidence}


def build_qt_release_checklist(
    *,
    backend_available: bool = False,
    tests_green: bool = False,
    page_readiness: Mapping[str, Any] | None = None,
    performance: Mapping[str, Any] | None = None,
    localization: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    readiness = dict(page_readiness or {})
    perf = dict(performance or {})
    loc = dict(localization or {})
    items = [
        _item("qt_backend", "Qt backend is available", passed=backend_available),
        _item("tests", "GUI model tests are green", passed=tests_green),
        _item("pages", "Primary pages are ready", passed=int(readiness.get("blocked_count", 1)) == 0, evidence=readiness),
        _item("performance", "Performance budgets are respected", passed=bool(perf.get("ok", False)), evidence=perf),
        _item("localization", "German UI has no obvious English leftovers", required=False, passed=bool(loc.get("ok", False)), evidence=loc),
    ]
    required = [item for item in items if item["required"]]
    passed_required = sum(1 for item in required if item["passed"])
    return {
        "schema_version": RELEASE_CHECKLIST_SCHEMA_VERSION,
        "kind": "qt_release_checklist",
        "ready_for_manual_smoke": passed_required == len(required),
        "required_count": len(required),
        "passed_required_count": passed_required,
        "item_count": len(items),
        "items": items,
    }


__all__ = ["RELEASE_CHECKLIST_SCHEMA_VERSION", "build_qt_release_checklist"]
