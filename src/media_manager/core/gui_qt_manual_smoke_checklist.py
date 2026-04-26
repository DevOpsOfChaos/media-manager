from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SMOKE_CHECKLIST_SCHEMA_VERSION = "1.0"

def build_qt_manual_smoke_checklist(*, language: str = "en", has_people_bundle: bool = False) -> dict[str, object]:
    de = str(language).lower().startswith("de")
    items = [
        ("launch", "GUI startet ohne Traceback" if de else "GUI launches without traceback"),
        ("navigate_dashboard", "Übersicht ist sichtbar" if de else "Dashboard is visible"),
        ("navigate_runs", "Laufhistorie öffnen" if de else "Open run history"),
        ("navigate_settings", "Einstellungen öffnen" if de else "Open settings"),
    ]
    if has_people_bundle:
        items.append(("people_review", "Personenprüfung mit Gruppen öffnen" if de else "Open people review with groups"))
    else:
        items.append(("people_empty", "Personenprüfung zeigt Empty State" if de else "People review shows empty state"))
    checks = [{"id": check_id, "label": label, "done": False, "required": True} for check_id, label in items]
    return {
        "schema_version": SMOKE_CHECKLIST_SCHEMA_VERSION,
        "kind": "qt_manual_smoke_checklist",
        "language": "de" if de else "en",
        "check_count": len(checks),
        "checks": checks,
    }

def mark_smoke_check_done(checklist: Mapping[str, Any], check_id: str) -> dict[str, object]:
    checks = []
    for raw in checklist.get("checks", []) if isinstance(checklist.get("checks"), list) else []:
        item = dict(raw) if isinstance(raw, Mapping) else {}
        if item.get("id") == check_id:
            item["done"] = True
        checks.append(item)
    return {
        **dict(checklist),
        "checks": checks,
        "done_count": sum(1 for item in checks if item.get("done")),
        "remaining_count": sum(1 for item in checks if not item.get("done") and item.get("required", True)),
    }

__all__ = ["SMOKE_CHECKLIST_SCHEMA_VERSION", "build_qt_manual_smoke_checklist", "mark_smoke_check_done"]
