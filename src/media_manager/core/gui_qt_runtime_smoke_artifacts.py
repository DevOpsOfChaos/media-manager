from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

QT_RUNTIME_SMOKE_ARTIFACTS_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: object, fallback: str = "") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _stable_hash(payload: Mapping[str, Any]) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def build_qt_runtime_smoke_artifact_record(
    artifact_id: str,
    *,
    path: str | Path,
    payload: Mapping[str, Any],
    artifact_type: str = "json",
    contains_sensitive_media: bool = False,
) -> dict[str, object]:
    target = Path(path)
    return {
        "schema_version": QT_RUNTIME_SMOKE_ARTIFACTS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_artifact_record",
        "artifact_id": _text(artifact_id, "artifact"),
        "artifact_type": _text(artifact_type, "json"),
        "path": str(target),
        "filename": target.name,
        "payload_kind": payload.get("kind"),
        "payload_hash": _stable_hash(payload),
        "contains_sensitive_media": bool(contains_sensitive_media),
        "metadata_only": not bool(contains_sensitive_media),
        "local_only": True,
    }


def build_qt_runtime_smoke_artifact_manifest(
    artifacts: Mapping[str, Mapping[str, Any]],
    *,
    root_dir: str | Path = ".",
) -> dict[str, object]:
    root = Path(root_dir)
    records = [
        build_qt_runtime_smoke_artifact_record(
            artifact_id,
            path=root / f"{artifact_id}.json",
            payload=payload,
            contains_sensitive_media=False,
        )
        for artifact_id, payload in sorted(artifacts.items())
        if isinstance(payload, Mapping)
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_ARTIFACTS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_artifact_manifest",
        "root_dir": str(root),
        "artifacts": records,
        "summary": {
            "artifact_count": len(records),
            "metadata_only_count": sum(1 for record in records if record.get("metadata_only")),
            "sensitive_media_count": sum(1 for record in records if record.get("contains_sensitive_media")),
            "all_local_only": all(record.get("local_only") for record in records),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = [
    "QT_RUNTIME_SMOKE_ARTIFACTS_SCHEMA_VERSION",
    "build_qt_runtime_smoke_artifact_manifest",
    "build_qt_runtime_smoke_artifact_record",
]
