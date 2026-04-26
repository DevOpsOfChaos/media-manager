from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

FOLDER_PICKER_SCHEMA_VERSION = "1.0"

_PICKER_LABELS = {
    "source": ("Source folder", "Choose a folder that contains media files."),
    "run_dir": ("Run history folder", "Choose the root folder that stores run artifacts."),
    "profile_dir": ("Profile folder", "Choose the folder that stores app profiles."),
    "people_bundle": ("People review bundle", "Choose a people review bundle folder."),
    "catalog": ("People catalog", "Choose a people catalog JSON file."),
}


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _path_payload(path: str | Path | None) -> dict[str, object]:
    if path is None or str(path).strip() == "":
        return {"path": "", "exists": False, "is_dir": False, "is_file": False}
    resolved = Path(path)
    return {
        "path": str(resolved),
        "exists": resolved.exists(),
        "is_dir": resolved.is_dir(),
        "is_file": resolved.is_file(),
    }


def build_folder_picker_model(
    picker_id: str,
    *,
    path: str | Path | None = None,
    recent_paths: Iterable[str | Path] = (),
    required: bool = False,
    must_exist: bool = False,
    allow_files: bool = False,
    allow_directories: bool = True,
) -> dict[str, object]:
    """Build a GUI path-picker contract without opening any native dialog."""
    label, description = _PICKER_LABELS.get(picker_id, (picker_id.replace("_", " ").title(), "Choose a local path."))
    value = _path_payload(path)
    recent = []
    seen: set[str] = set()
    for item in recent_paths:
        text = str(item).strip()
        if text and text not in seen:
            recent.append(_path_payload(text))
            seen.add(text)
    problems: list[dict[str, object]] = []
    if required and not value["path"]:
        problems.append({"code": "path_required", "severity": "warning", "message": f"{label} is required."})
    if must_exist and value["path"] and not value["exists"]:
        problems.append({"code": "path_missing", "severity": "error", "message": f"Path does not exist: {value['path']}"})
    if value["exists"]:
        if value["is_file"] and not allow_files:
            problems.append({"code": "file_not_allowed", "severity": "error", "message": "Expected a folder, got a file."})
        if value["is_dir"] and not allow_directories:
            problems.append({"code": "folder_not_allowed", "severity": "error", "message": "Expected a file, got a folder."})
    return {
        "schema_version": FOLDER_PICKER_SCHEMA_VERSION,
        "kind": "folder_picker",
        "picker_id": picker_id,
        "label": label,
        "description": description,
        "value": value,
        "required": required,
        "must_exist": must_exist,
        "allow_files": allow_files,
        "allow_directories": allow_directories,
        "recent_paths": recent[:12],
        "problem_count": len(problems),
        "problems": problems,
        "valid": not any(item["severity"] == "error" for item in problems),
    }


def build_standard_folder_pickers(*, source: str | Path | None = None, run_dir: str | Path | None = None, profile_dir: str | Path | None = None, people_bundle: str | Path | None = None) -> dict[str, object]:
    return {
        "schema_version": FOLDER_PICKER_SCHEMA_VERSION,
        "kind": "folder_picker_set",
        "pickers": [
            build_folder_picker_model("source", path=source),
            build_folder_picker_model("run_dir", path=run_dir),
            build_folder_picker_model("profile_dir", path=profile_dir),
            build_folder_picker_model("people_bundle", path=people_bundle),
        ],
    }


__all__ = ["FOLDER_PICKER_SCHEMA_VERSION", "build_folder_picker_model", "build_standard_folder_pickers"]
