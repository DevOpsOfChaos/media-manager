from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

PROFILE_CARDS_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_profile_card(profile: Mapping[str, Any]) -> dict[str, object]:
    valid = bool(profile.get("valid", True))
    return {
        "schema_version": PROFILE_CARDS_SCHEMA_VERSION,
        "kind": "profile_card",
        "profile_id": profile.get("profile_id"),
        "title": profile.get("title") or profile.get("profile_id") or "Profile",
        "command": profile.get("command"),
        "favorite": bool(profile.get("favorite")),
        "valid": valid,
        "status": "ready" if valid else "invalid",
        "path": profile.get("path"),
    }


def build_profile_cards(profiles: Iterable[Mapping[str, Any]] | None = None, *, limit: int = 12) -> dict[str, object]:
    raw = list(profiles or [])
    cards = [build_profile_card(_as_mapping(profile)) for profile in raw[: max(0, limit)]]
    return {
        "schema_version": PROFILE_CARDS_SCHEMA_VERSION,
        "kind": "profile_card_list",
        "cards": cards,
        "card_count": len(cards),
        "favorite_count": sum(1 for card in cards if card.get("favorite")),
        "invalid_count": sum(1 for card in cards if not card.get("valid")),
        "truncated": len(raw) > len(cards),
    }


__all__ = ["PROFILE_CARDS_SCHEMA_VERSION", "build_profile_card", "build_profile_cards"]
