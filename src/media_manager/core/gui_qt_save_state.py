from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

SAVE_STATE_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_workspace_save_state(
    *,
    workspace_path: str | Path | None = None,
    pending_change_count: int = 0,
    last_saved_at_utc: str | None = None,
    autosave_enabled: bool = True,
) -> dict[str, Any]:
    has_path = workspace_path is not None and str(workspace_path).strip() != ""
    pending = max(0, int(pending_change_count))
    return {
        "schema_version": SAVE_STATE_SCHEMA_VERSION,
        "workspace_path": str(workspace_path) if has_path else None,
        "has_workspace_path": has_path,
        "pending_change_count": pending,
        "has_unsaved_changes": pending > 0,
        "last_saved_at_utc": last_saved_at_utc,
        "autosave_enabled": bool(autosave_enabled),
        "save_action_enabled": has_path and pending > 0,
        "save_as_action_enabled": True,
    }


def write_workspace_save_state(path: str | Path, state: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(state)
    payload["saved_at_utc"] = _now_utc()
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def read_workspace_save_state(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object for GUI workspace save state.")
    return value


__all__ = ["SAVE_STATE_SCHEMA_VERSION", "build_workspace_save_state", "read_workspace_save_state", "write_workspace_save_state"]
