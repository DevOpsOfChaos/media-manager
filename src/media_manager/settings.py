from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

APP_DIR_NAME = "media-manager"
SETTINGS_FILE_NAME = "settings.json"


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


def save_app_settings(data: dict[str, Any]) -> None:
    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
