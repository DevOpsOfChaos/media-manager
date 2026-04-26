from __future__ import annotations

HELP_OVERLAY_SCHEMA_VERSION = "1.0"

_DEFAULT_SHORTCUTS = [
    ("Ctrl+K", "Open command palette"),
    ("Ctrl+1", "Dashboard"),
    ("Ctrl+3", "People review"),
    ("Esc", "Close dialog or overlay"),
]


def build_qt_help_overlay(*, language: str = "en", shortcuts: list[tuple[str, str]] | None = None) -> dict[str, object]:
    title = "Hilfe & Tastenkürzel" if str(language).startswith("de") else "Help & shortcuts"
    items = [{"shortcut": key, "description": desc} for key, desc in (shortcuts or _DEFAULT_SHORTCUTS)]
    return {"schema_version": HELP_OVERLAY_SCHEMA_VERSION, "title": title, "language": language, "item_count": len(items), "items": items}


__all__ = ["HELP_OVERLAY_SCHEMA_VERSION", "build_qt_help_overlay"]
