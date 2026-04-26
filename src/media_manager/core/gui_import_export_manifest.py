from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

IMPORT_EXPORT_SCHEMA_VERSION = "1.0"


def _path_entry(path: str | Path, *, role: str) -> dict[str, object]:
    resolved = Path(path)
    return {"path": str(resolved), "role": role, "exists": resolved.exists(), "is_sensitive": role in {"people_catalog", "people_report", "people_assets", "people_bundle"}}


def build_export_manifest(*, export_id: str, files: Iterable[Mapping[str, Any] | str | Path], privacy_level: str = "local_sensitive") -> dict[str, object]:
    entries = []
    for item in files:
        if isinstance(item, Mapping):
            path = item.get("path") or item.get("value")
            role = str(item.get("role") or "artifact")
            if path:
                entries.append(_path_entry(str(path), role=role))
        else:
            entries.append(_path_entry(item, role="artifact"))
    return {
        "schema_version": IMPORT_EXPORT_SCHEMA_VERSION,
        "kind": "gui_export_manifest",
        "export_id": export_id,
        "privacy_level": privacy_level,
        "file_count": len(entries),
        "sensitive_file_count": sum(1 for item in entries if item["is_sensitive"]),
        "files": entries,
        "safe_to_share": privacy_level == "public" and not any(item["is_sensitive"] for item in entries),
    }


def build_import_manifest(*, source_path: str | Path, expected_kind: str = "unknown") -> dict[str, object]:
    path = Path(source_path)
    return {
        "schema_version": IMPORT_EXPORT_SCHEMA_VERSION,
        "kind": "gui_import_manifest",
        "source_path": str(path),
        "expected_kind": expected_kind,
        "exists": path.exists(),
        "can_import": path.exists(),
    }


__all__ = ["IMPORT_EXPORT_SCHEMA_VERSION", "build_export_manifest", "build_import_manifest"]
