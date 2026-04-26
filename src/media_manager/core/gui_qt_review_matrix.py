from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_MATRIX_SCHEMA_VERSION = "1.0"
_STATUSES = ("needs_name", "needs_review", "ready_to_apply", "all_faces_rejected", "unknown")


def build_qt_review_matrix(groups: list[Mapping[str, Any]]) -> dict[str, object]:
    buckets = {status: [] for status in _STATUSES}
    for group in groups:
        status = str(group.get("status") or "unknown")
        if status not in buckets:
            status = "unknown"
        buckets[status].append(dict(group))
    cells = []
    for status in _STATUSES:
        items = buckets[status]
        cells.append({"status": status, "count": len(items), "group_ids": [item.get("group_id") for item in items if item.get("group_id")], "attention": status in {"needs_name", "needs_review"} and bool(items)})
    return {"schema_version": REVIEW_MATRIX_SCHEMA_VERSION, "group_count": sum(cell["count"] for cell in cells), "attention_count": sum(cell["count"] for cell in cells if cell["attention"]), "cells": cells}


__all__ = ["REVIEW_MATRIX_SCHEMA_VERSION", "build_qt_review_matrix"]
