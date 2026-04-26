from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

GUI_STATE_SCHEMA_VERSION = 1
DEFAULT_RECENT_LIMIT = 12


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def build_default_gui_state(*, workspace_root: str | Path | None = None) -> dict[str, Any]:
    """Return a stable local GUI state document.

    This file is intended for UI preferences and recent local paths only. It is
    not a report format and should remain small/readable.
    """
    created_at = _now_utc()
    return {
        "schema_version": GUI_STATE_SCHEMA_VERSION,
        "created_at_utc": created_at,
        "updated_at_utc": created_at,
        "workspace_root": str(workspace_root) if workspace_root is not None else None,
        "active_page_id": "dashboard",
        "recent": {
            "run_dirs": [],
            "profile_dirs": [],
            "people_bundle_dirs": [],
            "catalog_paths": [],
        },
        "people_review": {
            "last_bundle_dir": None,
            "last_catalog_path": None,
            "show_sensitive_encoding_warnings": True,
        },
        "preferences": {
            "confirm_destructive_actions": True,
            "open_last_workspace_on_start": True,
            "thumbnail_size": 256,
        },
    }


def load_gui_state(path: str | Path, *, workspace_root: str | Path | None = None) -> dict[str, Any]:
    state_path = Path(path)
    if not state_path.exists():
        return build_default_gui_state(workspace_root=workspace_root)
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected GUI state JSON object in {state_path}")
    if int(payload.get("schema_version", 0)) != GUI_STATE_SCHEMA_VERSION:
        raise ValueError(f"GUI state schema_version must be {GUI_STATE_SCHEMA_VERSION}")
    # Normalize additive sections for forward/backward compatibility.
    default = build_default_gui_state(workspace_root=workspace_root)
    for key in ("recent", "people_review", "preferences"):
        merged = dict(_as_mapping(default.get(key)))
        merged.update(dict(_as_mapping(payload.get(key))))
        payload[key] = merged
    payload.setdefault("active_page_id", default["active_page_id"])
    payload.setdefault("created_at_utc", default["created_at_utc"])
    payload.setdefault("updated_at_utc", default["updated_at_utc"])
    payload.setdefault("workspace_root", str(workspace_root) if workspace_root is not None else None)
    return payload


def write_gui_state(path: str | Path, state: Mapping[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(state)
    payload["schema_version"] = GUI_STATE_SCHEMA_VERSION
    payload["updated_at_utc"] = _now_utc()
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def set_active_page(state: Mapping[str, Any], page_id: str) -> dict[str, Any]:
    payload = dict(state)
    payload["active_page_id"] = str(page_id).strip() or "dashboard"
    payload["updated_at_utc"] = _now_utc()
    return payload


def add_recent_path(
    state: Mapping[str, Any],
    *,
    section: str,
    path: str | Path,
    limit: int = DEFAULT_RECENT_LIMIT,
) -> dict[str, Any]:
    """Add a path to a recent-list section, keeping order and de-duplicating."""
    value = _string_or_none(path)
    if value is None:
        return dict(state)
    payload = dict(state)
    recent = dict(_as_mapping(payload.get("recent")))
    current_raw = recent.get(section, [])
    current = [str(item) for item in current_raw] if isinstance(current_raw, list) else []
    normalized_existing = [item for item in current if item != value]
    recent[section] = [value, *normalized_existing][: max(1, int(limit))]
    payload["recent"] = recent
    payload["updated_at_utc"] = _now_utc()
    return payload


def register_people_bundle(
    state: Mapping[str, Any],
    *,
    bundle_dir: str | Path,
    catalog_path: str | Path | None = None,
) -> dict[str, Any]:
    payload = add_recent_path(state, section="people_bundle_dirs", path=bundle_dir)
    people_review = dict(_as_mapping(payload.get("people_review")))
    people_review["last_bundle_dir"] = str(bundle_dir)
    if catalog_path is not None:
        people_review["last_catalog_path"] = str(catalog_path)
        payload = add_recent_path(payload, section="catalog_paths", path=catalog_path)
    payload["people_review"] = people_review
    payload["active_page_id"] = "people-review"
    payload["updated_at_utc"] = _now_utc()
    return payload


def build_gui_state_summary(state: Mapping[str, Any]) -> dict[str, Any]:
    recent = _as_mapping(state.get("recent"))
    people = _as_mapping(state.get("people_review"))
    return {
        "schema_version": GUI_STATE_SCHEMA_VERSION,
        "active_page_id": state.get("active_page_id"),
        "workspace_root": state.get("workspace_root"),
        "recent_counts": {
            "run_dirs": len(recent.get("run_dirs", [])) if isinstance(recent.get("run_dirs"), list) else 0,
            "profile_dirs": len(recent.get("profile_dirs", [])) if isinstance(recent.get("profile_dirs"), list) else 0,
            "people_bundle_dirs": len(recent.get("people_bundle_dirs", [])) if isinstance(recent.get("people_bundle_dirs"), list) else 0,
            "catalog_paths": len(recent.get("catalog_paths", [])) if isinstance(recent.get("catalog_paths"), list) else 0,
        },
        "people_review": {
            "last_bundle_dir": people.get("last_bundle_dir"),
            "last_catalog_path": people.get("last_catalog_path"),
        },
    }


__all__ = [
    "DEFAULT_RECENT_LIMIT",
    "GUI_STATE_SCHEMA_VERSION",
    "add_recent_path",
    "build_default_gui_state",
    "build_gui_state_summary",
    "load_gui_state",
    "register_people_bundle",
    "set_active_page",
    "write_gui_state",
]
