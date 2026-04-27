from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MANIFEST_SCHEMA_VERSION = "1.0"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_qt_runtime_smoke_desktop_acceptance_manifest(
    bundle_summary: Mapping[str, Any],
    *,
    manifest_id: str = "runtime-smoke-desktop-acceptance",
    recorded_at_utc: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MANIFEST_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_manifest",
        "manifest_id": manifest_id,
        "recorded_at_utc": recorded_at_utc or _now(),
        "summary": dict(bundle_summary),
        "privacy": {
            "metadata_only": True,
            "contains_face_crops": False,
            "contains_embeddings": False,
            "contains_media_file_contents": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_MANIFEST_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_manifest"]
