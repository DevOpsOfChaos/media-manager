from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

COMMAND_PREVIEW_SCHEMA_VERSION = "1.0"
SENSITIVE_FLAGS = {"--include-encodings", "--apply", "--yes"}


def quote_command_part(value: object) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or any(ch in text for ch in '"\''):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def build_command_preview(argv: Iterable[object], *, label: str = "", risk_level: str = "safe") -> dict[str, object]:
    parts = [str(item) for item in argv]
    sensitive = [item for item in parts if item in SENSITIVE_FLAGS]
    return {
        "schema_version": COMMAND_PREVIEW_SCHEMA_VERSION,
        "kind": "command_preview",
        "label": label,
        "argv": parts,
        "command_line": " ".join(quote_command_part(item) for item in parts),
        "risk_level": risk_level,
        "requires_confirmation": bool(sensitive) or risk_level in {"medium", "high", "destructive"},
        "sensitive_flags": sensitive,
    }


def attach_command_preview(action: Mapping[str, Any], argv: Iterable[object]) -> dict[str, object]:
    return {**dict(action), "command_preview_model": build_command_preview(argv, label=str(action.get("label") or action.get("id") or ""), risk_level=str(action.get("risk_level") or "safe"))}


__all__ = ["COMMAND_PREVIEW_SCHEMA_VERSION", "SENSITIVE_FLAGS", "attach_command_preview", "build_command_preview", "quote_command_part"]
