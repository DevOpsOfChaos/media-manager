from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_mapping, as_text

QT_STATUS_PRESENTER_SCHEMA_VERSION = "1.0"


def build_qt_status_presenter(shell_model: Mapping[str, Any]) -> dict[str, object]:
    status = as_mapping(shell_model.get("status_bar"))
    page = as_mapping(shell_model.get("page"))
    notifications = as_mapping(shell_model.get("notifications"))
    diagnostics = as_mapping(shell_model.get("diagnostics"))
    return {
        "schema_version": QT_STATUS_PRESENTER_SCHEMA_VERSION,
        "kind": "qt_status_presenter",
        "text": as_text(status.get("text"), "Ready."),
        "active_page_id": as_text(shell_model.get("active_page_id"), as_text(page.get("page_id"))),
        "page_title": as_text(page.get("title")),
        "privacy_text": as_text(status.get("privacy")),
        "notification_count": notifications.get("message_count", 0),
        "diagnostic_error_count": diagnostics.get("error_count", 0),
        "safe_mode": True,
    }


__all__ = ["QT_STATUS_PRESENTER_SCHEMA_VERSION", "build_qt_status_presenter"]
