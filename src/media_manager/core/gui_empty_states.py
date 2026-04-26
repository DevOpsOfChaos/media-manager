from __future__ import annotations

from .gui_i18n import translate

EMPTY_STATE_SCHEMA_VERSION = "1.0"


def build_empty_state(page_id: str, *, language: str = "en", action_id: str | None = None) -> dict[str, object]:
    normalized = str(page_id or "dashboard").strip().lower()
    defaults = {
        "dashboard": ("No dashboard data yet.", "Create a profile or open a run folder."),
        "new-run": ("No profile selected.", "Choose a safe preview workflow to begin."),
        "people-review": (translate("people.empty", language=language), "Create a people review bundle from a scan report."),
        "run-history": (translate("run_history.empty", language=language), "Run a preview with --run-dir to see history here."),
        "profiles": ("No profiles found.", "Create a reusable profile for common tasks."),
        "settings": ("Settings are ready.", "Adjust language, theme, and privacy defaults."),
    }
    title, description = defaults.get(normalized, ("Nothing to show yet.", "This page is ready for a future iteration."))
    return {
        "schema_version": EMPTY_STATE_SCHEMA_VERSION,
        "page_id": normalized,
        "title": title,
        "description": description,
        "action": {"id": action_id or f"create_{normalized}", "label": translate("action.open", language=language)} if action_id else None,
    }


__all__ = ["EMPTY_STATE_SCHEMA_VERSION", "build_empty_state"]
