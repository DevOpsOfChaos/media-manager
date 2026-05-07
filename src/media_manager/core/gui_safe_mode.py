from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate

SAFE_MODE_SCHEMA_VERSION = "1.0"


def _as_bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def build_safe_mode_banner(
    *,
    safe_mode_enabled: bool = True,
    language: str = "en",
) -> dict[str, object]:
    """Build a persistent safe-mode banner for the GUI.

    When safe mode is enabled, no destructive operations are allowed.
    The banner reminds users that previews are safe.
    """

    return {
        "schema_version": SAFE_MODE_SCHEMA_VERSION,
        "kind": "safe_mode_banner",
        "enabled": safe_mode_enabled,
        "title": translate("safe_mode.enabled", language=language, fallback="Safe mode enabled"),
        "description": translate("safe_mode.description", language=language, fallback="No files will be deleted or modified."),
        "actions": [
            {
                "id": "disable_safe_mode",
                "label": translate("safe_mode.disable", language=language, fallback="Disable safe mode"),
                "enabled": safe_mode_enabled,
                "risk_level": "medium",
                "executes_immediately": False,
                "executes_commands": False,
            },
        ],
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
    }


def build_donation_prompt(
    *,
    run_count: int = 0,
    apply_count: int = 0,
    language: str = "en",
    dismissed: bool = False,
) -> dict[str, object] | None:
    """Build a friendly donation/support prompt.

    Shown after the user has applied operations successfully, as a
    non-intrusive nudge. Returns None if criteria not met or already dismissed.
    """

    if dismissed:
        return None
    if apply_count < 1 and run_count < 5:
        return None

    return {
        "schema_version": SAFE_MODE_SCHEMA_VERSION,
        "kind": "donation_prompt",
        "title": translate("donate.title", language=language, fallback="Support Media Manager"),
        "message": translate("donate.message", language=language, fallback="If this tool saved you hours of organizing, consider supporting development."),
        "actions": [
            {
                "id": "donate_coffee",
                "label": translate("donate.coffee", language=language, fallback="Buy me a coffee"),
                "url": "https://paypal.me/media-manager-donate",
                "icon": "coffee",
                "executes_immediately": False,
                "executes_commands": False,
            },
            {
                "id": "donate_tokens",
                "label": translate("donate.tokens", language=language, fallback="Send a few tokens"),
                "url": "https://paypal.me/media-manager-donate",
                "icon": "coins",
                "executes_immediately": False,
                "executes_commands": False,
            },
            {
                "id": "dismiss_donate",
                "label": translate("donate.dismiss", language=language, fallback="Maybe later"),
                "icon": "x",
                "executes_immediately": True,
                "executes_commands": False,
            },
        ],
        "run_count": run_count,
        "apply_count": apply_count,
    }


def build_safe_mode_status(
    home_state: Mapping[str, Any],
    *,
    language: str = "en",
) -> dict[str, object]:
    """Build the safe-mode status indicator for the shell/status bar."""

    safe_mode = _as_bool(home_state.get("safe_mode_enabled"), True)
    return {
        "schema_version": SAFE_MODE_SCHEMA_VERSION,
        "kind": "safe_mode_status",
        "safe_mode_enabled": safe_mode,
        "label": translate("safe_mode.enabled", language=language, fallback="Safe mode") if safe_mode else translate("safe_mode.disabled", language=language, fallback="Normal mode"),
        "icon": "shield-check" if safe_mode else "shield",
    }


__all__ = [
    "SAFE_MODE_SCHEMA_VERSION",
    "build_donation_prompt",
    "build_safe_mode_banner",
    "build_safe_mode_status",
]
