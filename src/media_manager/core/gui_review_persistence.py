from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any

PERSISTENCE_SCHEMA_VERSION = "1.0"


def read_gui_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def write_gui_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def build_review_persistence_manifest(
    *,
    workflow_path: str | Path | None = None,
    snapshot_path: str | Path | None = None,
    audit_log_path: str | Path | None = None,
    selection_path: str | Path | None = None,
) -> dict[str, object]:
    files = {
        "workflow": str(workflow_path) if workflow_path is not None else None,
        "snapshot": str(snapshot_path) if snapshot_path is not None else None,
        "audit_log": str(audit_log_path) if audit_log_path is not None else None,
        "selection": str(selection_path) if selection_path is not None else None,
    }
    return {
        "schema_version": PERSISTENCE_SCHEMA_VERSION,
        "kind": "gui_review_persistence_manifest",
        "files": files,
        "available_files": [key for key, value in files.items() if value],
        "safe_to_load": True,
    }


def save_review_workspace_state(
    *,
    root_dir: str | Path,
    snapshot: Mapping[str, Any],
    audit_log: Mapping[str, Any] | None = None,
    selection_state: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    root = Path(root_dir)
    snapshot_path = write_gui_json(root / "gui_workspace_snapshot.json", snapshot)
    audit_path = write_gui_json(root / "gui_review_audit_log.json", audit_log or {"events": [], "event_count": 0})
    selection_path = write_gui_json(root / "gui_selection_state.json", selection_state or {})
    manifest = build_review_persistence_manifest(snapshot_path=snapshot_path, audit_log_path=audit_path, selection_path=selection_path)
    manifest_path = write_gui_json(root / "gui_review_state_manifest.json", manifest)
    return {**manifest, "manifest_path": str(manifest_path)}


def load_review_workspace_state(manifest_path: str | Path) -> dict[str, object]:
    manifest = read_gui_json(manifest_path)
    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    loaded: dict[str, object] = {"manifest": manifest}
    for key, value in files.items():
        if isinstance(value, str) and value:
            path = Path(value)
            loaded[key] = read_gui_json(path) if path.exists() else None
    return loaded


__all__ = [
    "PERSISTENCE_SCHEMA_VERSION",
    "build_review_persistence_manifest",
    "load_review_workspace_state",
    "read_gui_json",
    "save_review_workspace_state",
    "write_gui_json",
]
