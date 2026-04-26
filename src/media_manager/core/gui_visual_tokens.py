from __future__ import annotations

from collections.abc import Mapping
from typing import Any

VISUAL_TOKENS_SCHEMA_VERSION = "1.0"

_DENSITY_SCALE = {
    "compact": 0.82,
    "comfortable": 1.0,
    "spacious": 1.18,
}

_DEFAULT_PALETTE = {
    "background": "#0f172a",
    "surface": "#111827",
    "surface_alt": "#1f2937",
    "text": "#e5e7eb",
    "muted": "#94a3b8",
    "accent": "#60a5fa",
    "accent_text": "#0f172a",
    "border": "#334155",
    "success": "#34d399",
    "warning": "#fbbf24",
    "danger": "#fb7185",
}


def _text(value: object, default: str = "") -> str:
    return value if isinstance(value, str) and value else default


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def normalize_density(density: str | None) -> str:
    value = str(density or "comfortable").strip().lower().replace("_", "-")
    return value if value in _DENSITY_SCALE else "comfortable"


def _scaled(base: int, density: str) -> int:
    return max(1, int(round(base * _DENSITY_SCALE[normalize_density(density)])))


def build_visual_tokens(*, theme_payload: Mapping[str, Any] | None = None, density: str | None = None) -> dict[str, object]:
    """Build renderer-facing visual tokens.

    The payload is intentionally plain JSON so Qt, web, or future native renderers
    can consume the same sizing/color contract.
    """

    theme = _mapping(theme_payload)
    palette = dict(_mapping(theme.get("palette")) or _mapping(theme.get("tokens")) or _DEFAULT_PALETTE)
    selected_density = normalize_density(density)
    return {
        "schema_version": VISUAL_TOKENS_SCHEMA_VERSION,
        "kind": "gui_visual_tokens",
        "density": selected_density,
        "theme": _text(theme.get("theme"), "modern-dark"),
        "palette": palette,
        "tokens": palette,  # compatibility alias for older generic renderers
        "spacing": {
            "xs": _scaled(6, selected_density),
            "sm": _scaled(10, selected_density),
            "md": _scaled(16, selected_density),
            "lg": _scaled(24, selected_density),
            "xl": _scaled(32, selected_density),
        },
        "radius": {
            "sm": _scaled(8, selected_density),
            "md": _scaled(14, selected_density),
            "lg": _scaled(20, selected_density),
            "xl": _scaled(28, selected_density),
        },
        "typography": {
            "font_family": _text(_mapping(theme.get("typography")).get("font_family"), "Segoe UI"),
            "title_size": _scaled(28, selected_density),
            "section_size": _scaled(20, selected_density),
            "body_size": _scaled(14, selected_density),
            "caption_size": _scaled(12, selected_density),
        },
        "component": {
            "card_min_height": _scaled(132, selected_density),
            "row_height": _scaled(44, selected_density),
            "sidebar_width": _scaled(268, selected_density),
            "thumbnail_size": _scaled(96, selected_density),
            "face_card_width": _scaled(180, selected_density),
        },
    }


def compact_visual_token_summary(tokens: Mapping[str, Any]) -> dict[str, object]:
    palette = _mapping(tokens.get("palette"))
    component = _mapping(tokens.get("component"))
    return {
        "schema_version": VISUAL_TOKENS_SCHEMA_VERSION,
        "density": tokens.get("density"),
        "theme": tokens.get("theme"),
        "has_background": "background" in palette,
        "has_accent": "accent" in palette,
        "sidebar_width": component.get("sidebar_width"),
        "thumbnail_size": component.get("thumbnail_size"),
    }


__all__ = [
    "VISUAL_TOKENS_SCHEMA_VERSION",
    "build_visual_tokens",
    "compact_visual_token_summary",
    "normalize_density",
]
