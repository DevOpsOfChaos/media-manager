from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

RUNTIME_CONFIG_SCHEMA_VERSION = "1.0"
SUPPORTED_BACKENDS = ("qt", "headless")
SUPPORTED_LANGUAGES = ("en", "de")
SUPPORTED_THEMES = ("modern-dark", "modern-light", "system")
SUPPORTED_DENSITIES = ("compact", "comfortable", "spacious")


def _text(value: object, default: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _choice(value: object, choices: tuple[str, ...], default: str) -> str:
    text = _text(value, default).lower().replace("_", "-")
    if text in choices:
        return text
    for choice in choices:
        if text.startswith(f"{choice}-"):
            return choice
    return default


def _path(value: object) -> str | None:
    text = _text(value)
    return str(Path(text)) if text else None


def build_qt_runtime_config(
    *,
    backend: str | None = "qt",
    language: str | None = "en",
    theme: str | None = "modern-dark",
    density: str | None = "comfortable",
    start_page_id: str | None = "dashboard",
    settings_path: str | Path | None = None,
    workspace_path: str | Path | None = None,
    people_bundle_dir: str | Path | None = None,
    safe_mode: bool = True,
    developer_mode: bool = False,
) -> dict[str, object]:
    """Return normalized launch configuration for the modern Qt GUI.

    This model intentionally does not launch the GUI. It is a stable contract for
    later runtime/bootstrap code and can be tested headlessly.
    """

    page = _text(start_page_id, "dashboard").lower().replace("_", "-")
    config = {
        "schema_version": RUNTIME_CONFIG_SCHEMA_VERSION,
        "kind": "qt_runtime_config",
        "backend": _choice(backend, SUPPORTED_BACKENDS, "qt"),
        "language": _choice(language, SUPPORTED_LANGUAGES, "en"),
        "theme": _choice(theme, SUPPORTED_THEMES, "modern-dark"),
        "density": _choice(density, SUPPORTED_DENSITIES, "comfortable"),
        "start_page_id": page or "dashboard",
        "settings_path": _path(settings_path),
        "workspace_path": _path(workspace_path),
        "people_bundle_dir": _path(people_bundle_dir),
        "safe_mode": bool(safe_mode),
        "developer_mode": bool(developer_mode),
    }
    config["summary"] = summarize_qt_runtime_config(config)
    return config


def summarize_qt_runtime_config(config: Mapping[str, Any]) -> dict[str, object]:
    return {
        "backend": config.get("backend", "qt"),
        "language": config.get("language", "en"),
        "theme": config.get("theme", "modern-dark"),
        "density": config.get("density", "comfortable"),
        "start_page_id": config.get("start_page_id", "dashboard"),
        "has_people_bundle": bool(config.get("people_bundle_dir")),
        "safe_mode": bool(config.get("safe_mode", True)),
        "developer_mode": bool(config.get("developer_mode", False)),
    }


def build_qt_launch_args(config: Mapping[str, Any]) -> list[str]:
    args = [
        "media-manager-gui",
        "--active-page",
        str(config.get("start_page_id") or "dashboard"),
        "--language",
        str(config.get("language") or "en"),
        "--theme",
        str(config.get("theme") or "modern-dark"),
        "--density",
        str(config.get("density") or "comfortable"),
    ]
    if config.get("people_bundle_dir"):
        args.extend(["--people-bundle-dir", str(config["people_bundle_dir"])])
    if config.get("settings_path"):
        args.extend(["--settings-json", str(config["settings_path"])])
    return args


__all__ = [
    "RUNTIME_CONFIG_SCHEMA_VERSION",
    "SUPPORTED_BACKENDS",
    "SUPPORTED_DENSITIES",
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_THEMES",
    "build_qt_launch_args",
    "build_qt_runtime_config",
    "summarize_qt_runtime_config",
]
