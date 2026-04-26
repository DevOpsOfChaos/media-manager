from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

VIEW_STATE_SCHEMA_VERSION = "1.0"
DEFAULT_ACTIVE_PAGE_ID = "dashboard"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_text(value: object, default: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _normalize_page_id(value: object) -> str:
    normalized = _as_text(value, DEFAULT_ACTIVE_PAGE_ID).lower().replace("_", "-")
    aliases = {
        "runs": "run-history",
        "run-history": "run-history",
        "people": "people-review",
        "people-review": "people-review",
        "new run": "new-run",
        "new-run": "new-run",
        "doctor": "settings",
    }
    return aliases.get(normalized, normalized or DEFAULT_ACTIVE_PAGE_ID)


def _unique_recent(values: list[object], *, limit: int = 12) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in values:
        text = _as_text(raw)
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
        if len(result) >= limit:
            break
    return result


@dataclass(slots=True)
class GuiViewState:
    active_page_id: str = DEFAULT_ACTIVE_PAGE_ID
    selected_group_id: str | None = None
    selected_face_id: str | None = None
    search_query: str = ""
    run_filter: str = "all"
    profile_filter: str = "all"
    people_filter: str = "all"
    recent_pages: list[str] = field(default_factory=list)
    recent_bundles: list[str] = field(default_factory=list)
    updated_at_utc: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": VIEW_STATE_SCHEMA_VERSION,
            "active_page_id": _normalize_page_id(self.active_page_id),
            "selected_group_id": self.selected_group_id,
            "selected_face_id": self.selected_face_id,
            "search_query": self.search_query,
            "run_filter": self.run_filter,
            "profile_filter": self.profile_filter,
            "people_filter": self.people_filter,
            "recent_pages": _unique_recent(self.recent_pages),
            "recent_bundles": _unique_recent(self.recent_bundles),
            "updated_at_utc": self.updated_at_utc or _now_utc(),
        }


def load_gui_view_state(path: str | Path | None) -> dict[str, object]:
    if path is None:
        return GuiViewState().to_dict()
    resolved = Path(path)
    if not resolved.exists():
        return GuiViewState().to_dict()
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"Expected GUI view-state JSON object in {resolved}")
    return normalize_gui_view_state(payload)


def normalize_gui_view_state(payload: Mapping[str, object] | None) -> dict[str, object]:
    source = payload or {}
    state = GuiViewState(
        active_page_id=_normalize_page_id(source.get("active_page_id")),
        selected_group_id=_as_text(source.get("selected_group_id")) or None,
        selected_face_id=_as_text(source.get("selected_face_id")) or None,
        search_query=_as_text(source.get("search_query")),
        run_filter=_as_text(source.get("run_filter"), "all"),
        profile_filter=_as_text(source.get("profile_filter"), "all"),
        people_filter=_as_text(source.get("people_filter"), "all"),
        recent_pages=_unique_recent(_as_list(source.get("recent_pages"))),
        recent_bundles=_unique_recent(_as_list(source.get("recent_bundles"))),
        updated_at_utc=_as_text(source.get("updated_at_utc")) or None,
    )
    return state.to_dict()


def update_gui_view_state(payload: Mapping[str, object] | None, **updates: object) -> dict[str, object]:
    state = normalize_gui_view_state(payload)
    if "active_page_id" in updates and updates["active_page_id"] is not None:
        page_id = _normalize_page_id(updates["active_page_id"])
        state["active_page_id"] = page_id
        state["recent_pages"] = _unique_recent([page_id, *_as_list(state.get("recent_pages"))])
    for key in ("selected_group_id", "selected_face_id", "search_query", "run_filter", "profile_filter", "people_filter"):
        if key in updates:
            value = updates[key]
            state[key] = _as_text(value) if value is not None else None
    if "people_bundle_dir" in updates and updates["people_bundle_dir"] is not None:
        state["recent_bundles"] = _unique_recent([_as_text(updates["people_bundle_dir"]), *_as_list(state.get("recent_bundles"))])
    state["updated_at_utc"] = _now_utc()
    return state


def write_gui_view_state(path: str | Path, payload: Mapping[str, object]) -> Path:
    normalized = normalize_gui_view_state(payload)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "DEFAULT_ACTIVE_PAGE_ID",
    "VIEW_STATE_SCHEMA_VERSION",
    "GuiViewState",
    "load_gui_view_state",
    "normalize_gui_view_state",
    "update_gui_view_state",
    "write_gui_view_state",
]
