from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(path: str | Path, payload: dict[str, Any]) -> Path:
    """Write a UTF-8 JSON report and return the normalized path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def build_review_file_payload(command_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Build a compact review-focused export from a command JSON payload."""
    result: dict[str, Any] = {
        "command": command_name,
        "sources": list(payload.get("sources", [])),
        "conflict_policy": payload.get("conflict_policy"),
        "include_patterns": list(payload.get("include_patterns", [])),
        "exclude_patterns": list(payload.get("exclude_patterns", [])),
        "outcome_report": payload.get("outcome_report"),
        "review": payload.get("review", {}),
    }
    for key in ("target_root", "pattern", "template", "organize_pattern", "rename_template"):
        if key in payload:
            result[key] = payload[key]
    if "execution" in payload:
        execution = payload["execution"]
        if isinstance(execution, dict):
            result["execution"] = {
                "apply_step": execution.get("apply_step"),
                "outcome_report": execution.get("outcome_report"),
            }
    return result


__all__ = ["build_review_file_payload", "write_json_report"]
