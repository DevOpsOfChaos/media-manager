from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RECENT_ITEMS_SCHEMA_VERSION = "1.0"
DEFAULT_RECENT_LIMIT = 12


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _normalize_path(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return str(Path(text).expanduser())
    except (OSError, RuntimeError):
        return text


def _item_key(item: Mapping[str, Any]) -> tuple[str, str]:
    return (_as_text(item.get("kind")).casefold(), _normalize_path(item.get("path")).casefold())


def build_recent_item(
    *,
    path: str | Path,
    kind: str,
    label: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    last_opened_at_utc: str | None = None,
) -> dict[str, object]:
    resolved = _normalize_path(path)
    display_label = label or (Path(resolved).name if resolved else str(kind))
    return {
        "schema_version": RECENT_ITEMS_SCHEMA_VERSION,
        "kind": str(kind),
        "path": resolved,
        "label": display_label,
        "exists": Path(resolved).exists() if resolved else False,
        "last_opened_at_utc": last_opened_at_utc or _now_utc(),
        "metadata": dict(metadata or {}),
    }


def normalize_recent_items(
    items: Iterable[Mapping[str, Any]],
    *,
    limit: int = DEFAULT_RECENT_LIMIT,
) -> list[dict[str, object]]:
    seen: set[tuple[str, str]] = set()
    normalized: list[dict[str, object]] = []
    for item in items:
        if not isinstance(item, Mapping):
            continue
        path = _normalize_path(item.get("path"))
        kind = _as_text(item.get("kind")) or "path"
        if not path:
            continue
        candidate = build_recent_item(
            path=path,
            kind=kind,
            label=_as_text(item.get("label")) or None,
            metadata=item.get("metadata") if isinstance(item.get("metadata"), Mapping) else {},
            last_opened_at_utc=_as_text(item.get("last_opened_at_utc")) or None,
        )
        key = _item_key(candidate)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(candidate)
        if len(normalized) >= max(0, int(limit)):
            break
    return normalized


def add_recent_item(
    items: Iterable[Mapping[str, Any]],
    *,
    path: str | Path,
    kind: str,
    label: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    limit: int = DEFAULT_RECENT_LIMIT,
) -> list[dict[str, object]]:
    candidate = build_recent_item(path=path, kind=kind, label=label, metadata=metadata)
    return normalize_recent_items([candidate, *list(items)], limit=limit)


def build_recent_items_state(
    *,
    recent_items: Iterable[Mapping[str, Any]] = (),
    limit: int = DEFAULT_RECENT_LIMIT,
) -> dict[str, object]:
    items = normalize_recent_items(recent_items, limit=limit)
    summary: dict[str, int] = {}
    for item in items:
        kind = _as_text(item.get("kind")) or "path"
        summary[kind] = summary.get(kind, 0) + 1
    return {
        "schema_version": RECENT_ITEMS_SCHEMA_VERSION,
        "kind": "recent_items_state",
        "limit": max(0, int(limit)),
        "item_count": len(items),
        "summary": dict(sorted(summary.items())),
        "items": items,
    }


__all__ = [
    "DEFAULT_RECENT_LIMIT",
    "RECENT_ITEMS_SCHEMA_VERSION",
    "add_recent_item",
    "build_recent_item",
    "build_recent_items_state",
    "normalize_recent_items",
]
