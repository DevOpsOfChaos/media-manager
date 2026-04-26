from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

PROGRESS_MODEL_SCHEMA_VERSION = "1.0"


def build_progress_stage(stage_id: str, label: str, *, complete: bool = False, active: bool = False, blocked: bool = False) -> dict[str, object]:
    return {
        "schema_version": PROGRESS_MODEL_SCHEMA_VERSION,
        "kind": "progress_stage",
        "stage_id": stage_id,
        "label": label,
        "complete": bool(complete),
        "active": bool(active),
        "blocked": bool(blocked),
        "status": "blocked" if blocked else "active" if active else "complete" if complete else "pending",
    }


def build_progress_model(stages: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    stage_list = [dict(stage) for stage in stages]
    total = len(stage_list)
    complete = sum(1 for stage in stage_list if stage.get("complete"))
    active = next((stage.get("stage_id") for stage in stage_list if stage.get("active")), None)
    if active is None:
        next_pending = next((stage for stage in stage_list if not stage.get("complete") and not stage.get("blocked")), None)
        active = next_pending.get("stage_id") if next_pending else None
    return {
        "schema_version": PROGRESS_MODEL_SCHEMA_VERSION,
        "kind": "progress_model",
        "stages": stage_list,
        "stage_count": total,
        "complete_count": complete,
        "active_stage_id": active,
        "percent": int(round((complete / total) * 100)) if total else 0,
        "blocked": any(stage.get("blocked") for stage in stage_list),
    }


__all__ = ["PROGRESS_MODEL_SCHEMA_VERSION", "build_progress_stage", "build_progress_model"]
