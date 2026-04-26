from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

SESSION_STORE_SCHEMA_VERSION = "1.0"
MAX_RECENT_ITEMS = 12


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dedupe(values: list[object], *, limit: int = MAX_RECENT_ITEMS) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= max(0, limit):
            break
    return result


def build_qt_session_state(
    *,
    active_page_id: str = "dashboard",
    window: Mapping[str, Any] | None = None,
    recent_people_bundles: list[object] | None = None,
    recent_run_dirs: list[object] | None = None,
    recent_profile_dirs: list[object] | None = None,
    last_search_query: str = "",
) -> dict[str, object]:
    window_payload = dict(window or {})
    return {
        "schema_version": SESSION_STORE_SCHEMA_VERSION,
        "kind": "qt_session_state",
        "updated_at_utc": _now_utc(),
        "active_page_id": str(active_page_id or "dashboard"),
        "window": {
            "width": int(window_payload.get("width", 1440)),
            "height": int(window_payload.get("height", 940)),
            "maximized": bool(window_payload.get("maximized", False)),
        },
        "recent": {
            "people_bundles": _dedupe(list(recent_people_bundles or [])),
            "run_dirs": _dedupe(list(recent_run_dirs or [])),
            "profile_dirs": _dedupe(list(recent_profile_dirs or [])),
        },
        "last_search_query": str(last_search_query or ""),
    }


def register_recent_item(session: Mapping[str, Any], *, category: str, value: str) -> dict[str, object]:
    payload = dict(session)
    recent = dict(payload.get("recent") if isinstance(payload.get("recent"), Mapping) else {})
    key = {
        "people_bundle": "people_bundles",
        "people_bundles": "people_bundles",
        "run_dir": "run_dirs",
        "run_dirs": "run_dirs",
        "profile_dir": "profile_dirs",
        "profile_dirs": "profile_dirs",
    }.get(category, category)
    values = [value, *list(recent.get(key, []))]
    recent[key] = _dedupe(values)
    payload["recent"] = recent
    payload["updated_at_utc"] = _now_utc()
    return payload


def write_qt_session_state(path: str | Path, session: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(session), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def read_qt_session_state(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Qt session state must be a JSON object.")
    if str(payload.get("schema_version")) != SESSION_STORE_SCHEMA_VERSION:
        raise ValueError(f"Qt session schema_version must be {SESSION_STORE_SCHEMA_VERSION}.")
    return payload


__all__ = [
    "MAX_RECENT_ITEMS",
    "SESSION_STORE_SCHEMA_VERSION",
    "build_qt_session_state",
    "read_qt_session_state",
    "register_recent_item",
    "write_qt_session_state",
]
