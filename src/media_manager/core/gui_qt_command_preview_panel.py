from __future__ import annotations

from collections.abc import Iterable

COMMAND_PREVIEW_PANEL_SCHEMA_VERSION = "1.0"
_RISKY = {"--apply", "--yes", "--delete", "--include-encodings"}


def build_qt_command_preview_panel(argv: Iterable[object], *, title: str = "Command preview") -> dict[str, object]:
    parts = [str(item) for item in argv if item is not None]
    risky = [item for item in parts if item in _RISKY]
    return {"schema_version": COMMAND_PREVIEW_PANEL_SCHEMA_VERSION, "title": title, "argv": parts, "command_preview": " ".join(parts), "risky_flags": risky, "requires_confirmation": bool(risky), "executes_immediately": False}


__all__ = ["COMMAND_PREVIEW_PANEL_SCHEMA_VERSION", "build_qt_command_preview_panel"]
