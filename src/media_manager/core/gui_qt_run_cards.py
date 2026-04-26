from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

RUN_CARDS_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_run_card(run: Mapping[str, Any]) -> dict[str, object]:
    exit_code = run.get("exit_code")
    status = "ok" if exit_code in (0, None) else "attention"
    return {
        "schema_version": RUN_CARDS_SCHEMA_VERSION,
        "kind": "run_card",
        "run_id": run.get("run_id"),
        "title": run.get("run_id") or "Run",
        "subtitle": run.get("command") or "unknown command",
        "status": run.get("status") or status,
        "exit_code": exit_code,
        "review_candidate_count": run.get("review_candidate_count", 0),
        "path": run.get("path"),
    }


def build_run_cards(runs: Iterable[Mapping[str, Any]] | None = None, *, limit: int = 8) -> dict[str, object]:
    raw = list(runs or [])
    cards = [build_run_card(_as_mapping(run)) for run in raw[: max(0, limit)]]
    return {
        "schema_version": RUN_CARDS_SCHEMA_VERSION,
        "kind": "run_card_list",
        "cards": cards,
        "card_count": len(cards),
        "attention_count": sum(1 for card in cards if card.get("status") in {"attention", "failed", "error"}),
        "truncated": len(raw) > len(cards),
    }


__all__ = ["RUN_CARDS_SCHEMA_VERSION", "build_run_card", "build_run_cards"]
