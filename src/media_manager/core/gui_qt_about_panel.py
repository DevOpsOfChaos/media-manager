from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ABOUT_PANEL_SCHEMA_VERSION = "1.0"


def build_qt_about_panel(manifest_summary: Mapping[str, Any] | None = None, *, version: str = "0.6.0") -> dict[str, object]:
    manifest = dict(manifest_summary or {})
    return {
        "schema_version": ABOUT_PANEL_SCHEMA_VERSION,
        "title": "Media Manager",
        "version": version,
        "subtitle": "Local-first media workflow assistant",
        "command_count": manifest.get("command_count", 0),
        "privacy": "Local people data and face crops should stay private.",
        "links": [{"id": "docs", "label": "Documentation", "enabled": False}],
    }


__all__ = ["ABOUT_PANEL_SCHEMA_VERSION", "build_qt_about_panel"]
