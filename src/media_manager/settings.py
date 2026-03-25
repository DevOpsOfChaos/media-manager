from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

APP_DIR_NAME = "media-manager"
SETTINGS_FILE_NAME = "settings.json"
DEFAULT_TARGET_TEMPLATE = "{year}/{month}"
DEFAULT_RENAME_TEMPLATE = "{year}{month}{day}_{hour}{minute}{second}_{stem}{suffix}"


def get_settings_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME}"


def get_settings_path() -> Path:
    return get_settings_dir() / SETTINGS_FILE_NAME


def load_app_settings() -> dict[str, Any]:
    path = get_settings_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _normalize_source_dirs(raw_sources: list[Any]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in raw_sources:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    return cleaned


def list_import_sets(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_sets = data.get("import_sets", [])
    if not isinstance(raw_sets, list):
        return []

    normalized: list[dict[str, Any]] = []
    for item in raw_sets:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        source_dirs_raw = item.get("source_dirs", [])
        if not name or not isinstance(source_dirs_raw, list):
            continue
        source_dirs = _normalize_source_dirs(source_dirs_raw)
        if not source_dirs:
            continue
        normalized.append(
            {
                "name": name,
                "source_dirs": source_dirs,
                "target_dir": str(item.get("target_dir", "")).strip(),
                "target_template": str(item.get("target_template", DEFAULT_TARGET_TEMPLATE)).strip()
                or DEFAULT_TARGET_TEMPLATE,
            }
        )

    return sorted(normalized, key=lambda entry: entry["name"].casefold())


def get_import_set(data: dict[str, Any], name: str) -> dict[str, Any] | None:
    needle = name.strip().casefold()
    for item in list_import_sets(data):
        if item["name"].casefold() == needle:
            return item
    return None


def upsert_import_set(
    data: dict[str, Any],
    name: str,
    source_dirs: list[str],
    target_dir: str,
    target_template: str,
) -> dict[str, Any]:
    clean_name = name.strip()
    clean_sources = _normalize_source_dirs(source_dirs)
    if not clean_name:
        raise ValueError("Import-set name must not be empty.")
    if not clean_sources:
        raise ValueError("Import sets require at least one source folder.")

    updated = dict(data)
    remaining = [
        item
        for item in list_import_sets(updated)
        if item["name"].casefold() != clean_name.casefold()
    ]
    remaining.append(
        {
            "name": clean_name,
            "source_dirs": clean_sources,
            "target_dir": target_dir.strip(),
            "target_template": target_template.strip() or DEFAULT_TARGET_TEMPLATE,
        }
    )
    updated["import_sets"] = sorted(remaining, key=lambda entry: entry["name"].casefold())
    return updated


def remove_import_set(data: dict[str, Any], name: str) -> dict[str, Any]:
    needle = name.strip().casefold()
    updated = dict(data)
    updated["import_sets"] = [
        item for item in list_import_sets(updated) if item["name"].casefold() != needle
    ]
    return updated


def save_app_settings(data: dict[str, Any]) -> None:
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
