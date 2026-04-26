from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LAYOUT_SCHEMA_VERSION = "1.0"
DEFAULT_DENSITY = "comfortable"
SUPPORTED_DENSITIES = ("compact", "comfortable", "spacious")

_DENSITY_TOKENS = {
    "compact": {"gap": 8, "padding": 12, "card_radius": 14, "font_scale": 0.92},
    "comfortable": {"gap": 14, "padding": 20, "card_radius": 18, "font_scale": 1.0},
    "spacious": {"gap": 22, "padding": 28, "card_radius": 24, "font_scale": 1.08},
}


def normalize_density(value: str | None) -> str:
    density = str(value or DEFAULT_DENSITY).strip().lower().replace("_", "-")
    return density if density in SUPPORTED_DENSITIES else DEFAULT_DENSITY


def build_layout_tokens(density: str | None = None) -> dict[str, object]:
    normalized = normalize_density(density)
    return {
        "schema_version": LAYOUT_SCHEMA_VERSION,
        "density": normalized,
        "supported_densities": list(SUPPORTED_DENSITIES),
        "tokens": dict(_DENSITY_TOKENS[normalized]),
        "breakpoints": {
            "narrow": 900,
            "medium": 1280,
            "wide": 1600,
        },
        "regions": {
            "sidebar_width": 292,
            "content_max_width": 1480,
            "people_review_detail_width": 420,
            "command_palette_width": 760,
        },
    }


def build_page_layout(page_id: str, *, density: str | None = None) -> dict[str, object]:
    tokens = build_layout_tokens(density)
    normalized = str(page_id or "dashboard").strip().lower()
    layout_by_page = {
        "dashboard": "hero_card_grid",
        "new-run": "guided_wizard",
        "people-review": "master_detail_gallery",
        "run-history": "filterable_table",
        "profiles": "profile_card_table",
        "settings": "settings_sections",
    }
    return {
        "schema_version": LAYOUT_SCHEMA_VERSION,
        "page_id": normalized,
        "layout": layout_by_page.get(normalized, "content_page"),
        "density": tokens["density"],
        "tokens": tokens["tokens"],
        "regions": tokens["regions"],
    }


def merge_layout(model: Mapping[str, Any], *, density: str | None = None) -> dict[str, object]:
    page_id = str(model.get("page_id") or model.get("active_page_id") or "dashboard")
    return {**dict(model), "layout_contract": build_page_layout(page_id, density=density)}


__all__ = [
    "DEFAULT_DENSITY",
    "LAYOUT_SCHEMA_VERSION",
    "SUPPORTED_DENSITIES",
    "build_layout_tokens",
    "build_page_layout",
    "merge_layout",
    "normalize_density",
]
