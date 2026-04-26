from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .app_services import build_app_home_state
from .gui_page_contracts import build_gui_navigation_state, build_gui_page_catalog
from .gui_state_store import build_default_gui_state, build_gui_state_summary, load_gui_state
from .people_review_bundle_validator import validate_people_review_bundle

STARTUP_SCHEMA_VERSION = 1


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_app_startup_state(
    *,
    gui_state_path: str | Path | None = None,
    profile_dir: str | Path | None = None,
    run_dir: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    active_page_id: str | None = None,
) -> dict[str, object]:
    """Build the first state object a future GUI can load at startup."""
    if gui_state_path is not None:
        try:
            gui_state = load_gui_state(gui_state_path)
            gui_state_loaded = Path(gui_state_path).exists()
            gui_state_error = None
        except Exception as exc:  # pragma: no cover - defensive startup path
            gui_state = build_default_gui_state()
            gui_state_loaded = False
            gui_state_error = str(exc)
    else:
        gui_state = build_default_gui_state()
        gui_state_loaded = False
        gui_state_error = None

    page_id = active_page_id or str(gui_state.get("active_page_id") or "dashboard")
    people_bundle = people_bundle_dir or _as_mapping(gui_state.get("people_review")).get("last_bundle_dir")
    home_state = build_app_home_state(
        profile_dir=profile_dir,
        run_dir=run_dir,
        people_bundle_dir=people_bundle,
        active_page_id=page_id,
    )
    bundle_validation = validate_people_review_bundle(people_bundle) if people_bundle else None
    return {
        "schema_version": STARTUP_SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "kind": "app_startup_state",
        "active_page_id": page_id,
        "gui_state_path": str(gui_state_path) if gui_state_path is not None else None,
        "gui_state_loaded": gui_state_loaded,
        "gui_state_error": gui_state_error,
        "gui_state_summary": build_gui_state_summary(gui_state),
        "navigation": build_gui_navigation_state(page_id),
        "pages": build_gui_page_catalog(),
        "home_state": home_state,
        "people_bundle_validation": bundle_validation,
        "startup_checks": {
            "profile_dir_exists": Path(profile_dir).exists() if profile_dir is not None else None,
            "run_dir_exists": Path(run_dir).exists() if run_dir is not None else None,
            "people_bundle_dir_exists": Path(people_bundle).exists() if people_bundle else None,
        },
        "next_action": (
            "Open the people review page."
            if bundle_validation is not None and bundle_validation.get("ready_for_gui")
            else "Open the dashboard."
        ),
    }


__all__ = ["STARTUP_SCHEMA_VERSION", "build_app_startup_state"]
