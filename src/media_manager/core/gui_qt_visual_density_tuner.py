from __future__ import annotations

DENSITY_TUNER_SCHEMA_VERSION = "1.0"

_DENSITIES = {
    "compact": {"card_padding": 12, "grid_gap": 10, "row_height": 30, "face_card_size": 96, "columns": 4},
    "comfortable": {"card_padding": 18, "grid_gap": 16, "row_height": 38, "face_card_size": 132, "columns": 3},
    "spacious": {"card_padding": 24, "grid_gap": 22, "row_height": 46, "face_card_size": 168, "columns": 2},
}


def normalize_density(density: str | None) -> str:
    value = str(density or "comfortable").strip().lower()
    return value if value in _DENSITIES else "comfortable"


def build_density_tuning(density: str | None = None, *, page_id: str = "dashboard") -> dict[str, object]:
    normalized = normalize_density(density)
    tokens = dict(_DENSITIES[normalized])
    if page_id == "people-review":
        tokens["columns"] = max(1, int(tokens["columns"]) - 1)
        tokens["face_card_size"] = int(tokens["face_card_size"]) + 8
    return {
        "schema_version": DENSITY_TUNER_SCHEMA_VERSION,
        "density": normalized,
        "page_id": page_id,
        "tokens": tokens,
        "summary": f"{normalized}: {tokens['columns']} columns, face cards {tokens['face_card_size']}px",
    }


def build_density_options() -> dict[str, object]:
    return {
        "schema_version": DENSITY_TUNER_SCHEMA_VERSION,
        "default": "comfortable",
        "options": [{"id": key, "tokens": dict(value)} for key, value in sorted(_DENSITIES.items())],
    }


__all__ = ["DENSITY_TUNER_SCHEMA_VERSION", "build_density_options", "build_density_tuning", "normalize_density"]
