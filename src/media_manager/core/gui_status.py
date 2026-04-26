from __future__ import annotations

from collections.abc import Mapping
from typing import Any

STATUS_SCHEMA_VERSION = "1.0"


def build_gui_status(*, severity: str = "info", message: str = "Ready.", details: Mapping[str, Any] | None = None) -> dict[str, object]:
    normalized = str(severity or "info").lower()
    if normalized not in {"info", "success", "warning", "error"}:
        normalized = "info"
    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "severity": normalized,
        "message": str(message or "Ready."),
        "details": dict(details or {}),
    }


def status_from_missing_qt(guidance: str) -> dict[str, object]:
    return build_gui_status(severity="error", message="Modern GUI backend is not installed.", details={"install_guidance": guidance})


def status_from_model(model: Mapping[str, Any]) -> dict[str, object]:
    status_bar = model.get("status_bar") if isinstance(model.get("status_bar"), Mapping) else {}
    return build_gui_status(message=str(status_bar.get("text") or "Ready."), details={"privacy": status_bar.get("privacy")})


__all__ = ["STATUS_SCHEMA_VERSION", "build_gui_status", "status_from_missing_qt", "status_from_model"]
