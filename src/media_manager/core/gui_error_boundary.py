from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ERROR_BOUNDARY_SCHEMA_VERSION = "1.0"


def build_gui_error(code: str, message: str, *, severity: str = "error", recoverable: bool = True, details: Mapping[str, Any] | None = None) -> dict[str, object]:
    return {
        "schema_version": ERROR_BOUNDARY_SCHEMA_VERSION,
        "kind": "gui_error",
        "code": code,
        "message": message,
        "severity": severity,
        "recoverable": recoverable,
        "details": dict(details or {}),
    }


def error_from_exception(exc: BaseException, *, code: str = "unexpected_error", recoverable: bool = True) -> dict[str, object]:
    return build_gui_error(code, f"{type(exc).__name__}: {exc}", recoverable=recoverable)


def build_error_boundary(errors: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    items = [dict(item) for item in errors]
    return {
        "schema_version": ERROR_BOUNDARY_SCHEMA_VERSION,
        "kind": "error_boundary",
        "error_count": len(items),
        "blocking_count": sum(1 for item in items if not bool(item.get("recoverable", True))),
        "warning_count": sum(1 for item in items if item.get("severity") == "warning"),
        "errors": items,
        "can_continue": not any(not bool(item.get("recoverable", True)) for item in items),
    }


__all__ = ["ERROR_BOUNDARY_SCHEMA_VERSION", "build_gui_error", "error_from_exception", "build_error_boundary"]
