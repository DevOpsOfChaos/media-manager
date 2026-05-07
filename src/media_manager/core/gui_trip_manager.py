from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_empty_states import build_empty_state
from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_card

TRIP_MANAGER_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def build_trip_card(
    trip_id: str,
    label: str,
    *,
    start_date: str = "",
    end_date: str = "",
    file_count: int = 0,
    mode: str = "link",
    target_path: str = "",
) -> dict[str, object]:
    return {
        "id": trip_id,
        "component": "trip_card",
        "label": label,
        "start_date": start_date,
        "end_date": end_date,
        "file_count": file_count,
        "mode": mode,
        "mode_label": {"link": "Hard links", "copy": "Copies"}.get(mode, mode),
        "target_path": target_path,
        "actions": [
            build_action_button("open_trip", "Open", variant="primary", icon="folder-open"),
            build_action_button("delete_trip", "Remove", variant="danger", icon="trash"),
        ],
    }


def build_trip_manager_page_model(
    home_state: Mapping[str, Any],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build the trip management page: browse existing trips and create new ones."""

    home = _as_mapping(home_state)
    trips_raw = _as_list(home.get("trips") or home.get("trip_list") or [])
    trips: list[dict[str, object]] = []
    for item in trips_raw:
        if not isinstance(item, Mapping):
            continue
        trips.append(
            build_trip_card(
                trip_id=_text(item.get("trip_id") or item.get("label")),
                label=_text(item.get("label"), "Unnamed trip"),
                start_date=_text(item.get("start_date") or item.get("start")),
                end_date=_text(item.get("end_date") or item.get("end")),
                file_count=_as_int(item.get("file_count") or item.get("selected_count")),
                mode=_text(item.get("mode"), "link"),
                target_path=_text(item.get("target_path") or item.get("target_root")),
            )
        )

    return {
        "schema_version": TRIP_MANAGER_SCHEMA_VERSION,
        "page_id": "trip-manager",
        "title": translate("trip.manager.title", language=language, fallback="Trip Manager"),
        "description": translate("trip.manager.description", language=language, fallback="Browse, create, and manage your trip collections."),
        "kind": "trip_manager_page",
        "trips": trips,
        "trip_count": len(trips),
        "actions": [
            build_action_button("new_trip", translate("trip.action.new", language=language, fallback="New trip"), variant="primary", icon="map-pin"),
            build_action_button("browse_trips", translate("trip.action.browse", language=language, fallback="Browse all trips"), variant="secondary", icon="folder-open"),
        ],
        "quick_create": {
            "title": translate("trip.quick.title", language=language, fallback="Quick create"),
            "description": translate("trip.quick.description", language=language, fallback="Select a date range and source folder to create a new trip collection."),
            "fields": [
                {"id": "trip_label", "label": translate("trip.field.label", language=language, fallback="Trip name"), "type": "text", "required": True, "placeholder": "e.g. Italy 2025"},
                {"id": "trip_start", "label": translate("trip.field.start", language=language, fallback="Start date"), "type": "date", "required": True},
                {"id": "trip_end", "label": translate("trip.field.end", language=language, fallback="End date"), "type": "date", "required": True},
                {"id": "trip_source", "label": translate("trip.field.source", language=language, fallback="Source folder"), "type": "folder_picker", "required": True},
                {"id": "trip_target", "label": translate("trip.field.target", language=language, fallback="Trip target root"), "type": "folder_picker", "required": True},
            ],
            "mode_options": [
                {"id": "link", "label": translate("trip.mode.link", language=language, fallback="Hard links (no extra space)"), "default": True},
                {"id": "copy", "label": translate("trip.mode.copy", language=language, fallback="Copies (portable)")},
            ],
        },
        "organization_options": {
            "title": translate("trip.org.title", language=language, fallback="Organization style"),
            "description": translate("trip.org.description", language=language, fallback="How should your media library be structured?"),
            "options": [
                {"id": "date_hierarchy", "label": "Year / Month / Day", "description": translate("trip.org.date_hierarchy", language=language, fallback="Standard date-based folder structure.")},
                {"id": "trips_only", "label": "Trips only", "description": translate("trip.org.trips_only", language=language, fallback="Organize everything by trip, no date folders.")},
                {"id": "hybrid", "label": "Hybrid", "description": translate("trip.org.hybrid", language=language, fallback="Date structure + separate trip folders with links.")},
            ],
        },
        "empty_state": build_empty_state("trip-manager", language=language) if not trips else None,
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
    }
