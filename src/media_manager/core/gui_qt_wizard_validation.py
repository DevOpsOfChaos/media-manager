from __future__ import annotations

from collections.abc import Mapping
from typing import Any

WIZARD_VALIDATION_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def validate_new_run_wizard(values: Mapping[str, Any]) -> dict[str, object]:
    command = str(values.get("command") or "").strip().lower()
    sources = [str(item).strip() for item in _list(values.get("source_dirs") or values.get("sources")) if str(item).strip()]
    problems: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    if command not in {"organize", "rename", "duplicates", "cleanup", "people", "doctor"}:
        problems.append({"code": "command_missing", "message": "Choose a supported command.", "severity": "error"})
    if command in {"organize", "rename", "duplicates", "cleanup", "people"} and not sources:
        problems.append({"code": "sources_missing", "message": "Add at least one source folder.", "severity": "error"})
    if command in {"organize", "cleanup"} and not str(values.get("target") or values.get("target_root") or "").strip():
        problems.append({"code": "target_missing", "message": "Choose a target folder.", "severity": "error"})
    if command == "people" and values.get("include_encodings"):
        warnings.append({"code": "sensitive_encodings", "message": "Face encodings are sensitive biometric metadata.", "severity": "warning"})
    if values.get("apply") or values.get("yes"):
        problems.append({"code": "apply_not_allowed_in_wizard_preview", "message": "The GUI wizard starts in preview mode.", "severity": "error"})
    return {
        "schema_version": WIZARD_VALIDATION_SCHEMA_VERSION,
        "kind": "qt_wizard_validation",
        "command": command,
        "valid": not problems,
        "problems": problems,
        "warnings": warnings,
        "problem_count": len(problems),
        "warning_count": len(warnings),
        "ready_for_preview": not problems,
    }


__all__ = ["WIZARD_VALIDATION_SCHEMA_VERSION", "validate_new_run_wizard"]
