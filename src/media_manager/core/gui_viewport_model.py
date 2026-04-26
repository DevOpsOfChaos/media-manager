from __future__ import annotations

from typing import Any, Mapping

VIEWPORT_SCHEMA_VERSION = "1.0"
DEFAULT_VIEWPORT = {"width": 1280, "height": 800, "density": "comfortable"}
SUPPORTED_DENSITIES = ("compact", "comfortable", "spacious")

_BREAKPOINTS = [
    (0, "xs"),
    (640, "sm"),
    (900, "md"),
    (1200, "lg"),
    (1600, "xl"),
]

_DENSITY_CARD_WIDTH = {
    "compact": 220,
    "comfortable": 280,
    "spacious": 340,
}


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_density(value: str | None) -> str:
    density = str(value or DEFAULT_VIEWPORT["density"]).strip().lower()
    return density if density in SUPPORTED_DENSITIES else str(DEFAULT_VIEWPORT["density"])


def breakpoint_for_width(width: int) -> str:
    selected = "xs"
    for minimum, name in _BREAKPOINTS:
        if width >= minimum:
            selected = name
    return selected


def normalize_viewport(
    viewport: Mapping[str, Any] | None = None,
    *,
    width: int | None = None,
    height: int | None = None,
    density: str | None = None,
) -> dict[str, object]:
    payload = dict(viewport or {})
    resolved_width = max(320, _as_int(width if width is not None else payload.get("width"), int(DEFAULT_VIEWPORT["width"])))
    resolved_height = max(240, _as_int(height if height is not None else payload.get("height"), int(DEFAULT_VIEWPORT["height"])))
    resolved_density = normalize_density(density or payload.get("density"))
    breakpoint = breakpoint_for_width(resolved_width)
    min_card_width = _DENSITY_CARD_WIDTH[resolved_density]
    columns = max(1, min(5, resolved_width // min_card_width))
    return {
        "schema_version": VIEWPORT_SCHEMA_VERSION,
        "width": resolved_width,
        "height": resolved_height,
        "density": resolved_density,
        "breakpoint": breakpoint,
        "orientation": "landscape" if resolved_width >= resolved_height else "portrait",
        "is_compact": breakpoint in {"xs", "sm"},
        "min_card_width": min_card_width,
        "recommended_columns": columns,
    }


def choose_column_count(viewport: Mapping[str, Any] | None = None, *, item_count: int | None = None, max_columns: int = 5) -> int:
    normalized = normalize_viewport(viewport)
    columns = int(normalized["recommended_columns"])
    if item_count is not None:
        columns = min(columns, max(1, int(item_count)))
    return max(1, min(max(1, int(max_columns)), columns))


__all__ = [
    "DEFAULT_VIEWPORT",
    "SUPPORTED_DENSITIES",
    "VIEWPORT_SCHEMA_VERSION",
    "breakpoint_for_width",
    "choose_column_count",
    "normalize_density",
    "normalize_viewport",
]
