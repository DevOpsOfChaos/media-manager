from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

HEATMAP_SCHEMA_VERSION = "1.0"


def _status(group: Mapping[str, Any]) -> str:
    return str(group.get("status") or "unknown")


def _face_count(group: Mapping[str, Any]) -> int:
    counts = group.get("counts")
    if isinstance(counts, Mapping):
        return int(counts.get("face_count", group.get("face_count", 0)) or 0)
    return int(group.get("face_count", 0) or 0)


def build_people_review_heatmap(groups: Iterable[Mapping[str, Any]], *, bucket_size: int = 5) -> dict[str, object]:
    rows: dict[str, dict[str, int]] = {}
    for group in groups:
        status = _status(group)
        faces = _face_count(group)
        bucket_start = (faces // max(1, bucket_size)) * max(1, bucket_size)
        bucket = f"{bucket_start}-{bucket_start + max(1, bucket_size) - 1}"
        rows.setdefault(status, {})
        rows[status][bucket] = rows[status].get(bucket, 0) + 1
    cells = [
        {"status": status, "bucket": bucket, "count": count}
        for status, buckets in sorted(rows.items())
        for bucket, count in sorted(buckets.items())
    ]
    return {
        "schema_version": HEATMAP_SCHEMA_VERSION,
        "kind": "people_review_heatmap",
        "bucket_size": max(1, bucket_size),
        "cell_count": len(cells),
        "total_group_count": sum(cell["count"] for cell in cells),
        "cells": cells,
    }


__all__ = ["HEATMAP_SCHEMA_VERSION", "build_people_review_heatmap"]
