from __future__ import annotations

from collections.abc import Mapping
from typing import Any

TASK_CARD_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_task_card(card_id: str, title: str, *, kind: str, status: str = "todo", metrics: Mapping[str, Any] | None = None, action_id: str | None = None) -> dict[str, object]:
    return {
        "schema_version": TASK_CARD_SCHEMA_VERSION,
        "kind": "task_card",
        "card_id": card_id,
        "task_kind": kind,
        "title": title,
        "status": status,
        "metrics": dict(metrics or {}),
        "action_id": action_id,
    }


def task_cards_from_home_state(home_state: Mapping[str, Any]) -> dict[str, object]:
    profiles = _mapping(_mapping(home_state.get("profiles")).get("summary"))
    runs = _mapping(_mapping(home_state.get("runs")).get("summary"))
    people = _mapping(home_state.get("people_review"))
    people_summary = _mapping(people.get("summary"))
    cards = [
        build_task_card("profiles", "Profiles", kind="profiles", status="ready", metrics={"profiles": profiles.get("profile_count", 0), "valid": profiles.get("valid_count", 0)}, action_id="open_profiles"),
        build_task_card("runs", "Run history", kind="runs", status="ready", metrics={"runs": runs.get("run_count", 0), "errors": runs.get("error_count", 0)}, action_id="open_runs"),
        build_task_card("people", "People review", kind="people_review", status="ready" if people.get("ready_for_gui") else "todo", metrics={"groups": people_summary.get("group_count", 0), "faces": people_summary.get("face_count", 0)}, action_id="open_people_review"),
    ]
    return {
        "schema_version": TASK_CARD_SCHEMA_VERSION,
        "kind": "task_card_collection",
        "cards": cards,
        "card_count": len(cards),
        "ready_count": sum(1 for card in cards if card["status"] == "ready"),
    }


__all__ = ["TASK_CARD_SCHEMA_VERSION", "build_task_card", "task_cards_from_home_state"]
