from __future__ import annotations

from collections.abc import Mapping
from typing import Any

THEME_ADAPTER_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_qt_theme_adapter_payload(theme_payload: Mapping[str, Any]) -> dict[str, object]:
    palette = dict(_mapping(theme_payload.get("palette") or theme_payload.get("tokens")))
    roles = {
        "window": palette.get("background", "#0f172a"),
        "panel": palette.get("surface", "#111827"),
        "panel_alt": palette.get("surface_alt", "#1f2937"),
        "text": palette.get("text", "#e5e7eb"),
        "muted_text": palette.get("muted", "#94a3b8"),
        "accent": palette.get("accent", "#60a5fa"),
        "danger": palette.get("danger", "#fb7185"),
    }
    return {
        "schema_version": THEME_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_theme_adapter_payload",
        "theme": theme_payload.get("theme", "modern-dark"),
        "roles": roles,
        "stylesheet_placeholders": {f"{{{{{key}}}}}": value for key, value in roles.items()},
        "compatible_with_legacy_tokens": bool(theme_payload.get("tokens")),
    }

def validate_qt_theme_adapter(payload: Mapping[str, Any]) -> dict[str, object]:
    roles = _mapping(payload.get("roles"))
    required = {"window", "panel", "text", "accent"}
    missing = sorted(required - set(str(key) for key in roles))
    return {"valid": not missing, "missing_roles": missing, "role_count": len(roles)}

__all__ = ["THEME_ADAPTER_SCHEMA_VERSION", "build_qt_theme_adapter_payload", "validate_qt_theme_adapter"]
