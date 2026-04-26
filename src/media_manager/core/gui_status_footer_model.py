from __future__ import annotations

from collections.abc import Mapping
from typing import Any

STATUS_FOOTER_SCHEMA_VERSION = "1.0"


def build_status_footer(*, active_page_id: str = "dashboard", notifications: Mapping[str, Any] | None = None, diagnostics: Mapping[str, Any] | None = None, safe_mode: bool = True, language: str = "en") -> dict[str, object]:
    notification_count = int((notifications or {}).get("notification_count", (notifications or {}).get("message_count", 0)) or 0)
    diagnostic_errors = int((diagnostics or {}).get("error_count", 0) or 0)
    diagnostic_warnings = int((diagnostics or {}).get("warning_count", 0) or 0)
    status = "error" if diagnostic_errors else "warning" if diagnostic_warnings else "ready"
    return {
        "schema_version": STATUS_FOOTER_SCHEMA_VERSION,
        "kind": "status_footer",
        "active_page_id": active_page_id,
        "language": language,
        "status": status,
        "safe_mode": safe_mode,
        "notification_count": notification_count,
        "diagnostic_error_count": diagnostic_errors,
        "diagnostic_warning_count": diagnostic_warnings,
        "text": "Safe preview mode" if safe_mode else "Apply mode requires confirmation",
    }


__all__ = ["STATUS_FOOTER_SCHEMA_VERSION", "build_status_footer"]
