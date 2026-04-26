from __future__ import annotations

from collections.abc import Iterable, Mapping
from hashlib import sha256
import json
from typing import Any

VISUAL_REGRESSION_SCHEMA_VERSION = "1.0"


def _stable_digest(payload: Mapping[str, Any]) -> str:
    text = json.dumps(dict(payload), sort_keys=True, ensure_ascii=False, default=str)
    return sha256(text.encode("utf-8")).hexdigest()[:16]


def build_visual_regression_manifest(models: Iterable[Mapping[str, Any]], *, suite_id: str = "qt-product") -> dict[str, object]:
    snapshots = []
    for index, model in enumerate(models, start=1):
        kind = str(model.get("kind") or model.get("page_id") or "model")
        snapshots.append({"index": index, "kind": kind, "digest": _stable_digest(model), "key_count": len(model.keys())})
    return {
        "schema_version": VISUAL_REGRESSION_SCHEMA_VERSION,
        "kind": "qt_visual_regression_manifest",
        "suite_id": suite_id,
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
    }


__all__ = ["VISUAL_REGRESSION_SCHEMA_VERSION", "build_visual_regression_manifest"]
