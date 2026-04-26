from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

RENDER_SNAPSHOT_SCHEMA_VERSION = "1.0"


def stable_json_digest(payload: Mapping[str, Any], *, length: int = 16) -> str:
    data = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha1(data).hexdigest()[: max(4, min(40, int(length)))]


def build_render_snapshot(payload: Mapping[str, Any], *, label: str = "") -> dict[str, object]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    return {
        "schema_version": RENDER_SNAPSHOT_SCHEMA_VERSION,
        "kind": "gui_render_snapshot",
        "label": label,
        "digest": stable_json_digest(payload),
        "top_level_keys": sorted(str(key) for key in payload.keys()),
        "summary": dict(summary),
        "payload_kind": payload.get("kind"),
        "page_id": payload.get("page_id"),
    }


def compare_render_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, object]:
    before_digest = before.get("digest") or stable_json_digest(before)
    after_digest = after.get("digest") or stable_json_digest(after)
    return {
        "schema_version": RENDER_SNAPSHOT_SCHEMA_VERSION,
        "kind": "gui_render_snapshot_compare",
        "changed": before_digest != after_digest,
        "before_digest": before_digest,
        "after_digest": after_digest,
    }


__all__ = ["RENDER_SNAPSHOT_SCHEMA_VERSION", "build_render_snapshot", "compare_render_snapshots", "stable_json_digest"]
