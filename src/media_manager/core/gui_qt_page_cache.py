from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PAGE_CACHE_SCHEMA_VERSION = "1.0"


def _cache_key(page_id: str, *, language: str = "en", density: str = "comfortable", query: str = "") -> str:
    return f"{page_id}|{language}|{density}|{query}"


def build_page_cache_entry(page_id: str, page_plan: Mapping[str, Any], *, language: str = "en", density: str = "comfortable", query: str = "") -> dict[str, object]:
    return {
        "schema_version": PAGE_CACHE_SCHEMA_VERSION,
        "kind": "page_cache_entry",
        "key": _cache_key(page_id, language=language, density=density, query=query),
        "page_id": page_id,
        "language": language,
        "density": density,
        "query": query,
        "plan": dict(page_plan),
    }


def build_page_cache(entries: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    rows = [dict(item) for item in (entries or [])]
    return {
        "schema_version": PAGE_CACHE_SCHEMA_VERSION,
        "kind": "qt_page_cache",
        "entry_count": len(rows),
        "keys": [str(item.get("key")) for item in rows],
        "entries": rows,
    }


def find_cached_page(cache: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    for entry in cache.get("entries", []) if isinstance(cache.get("entries"), list) else []:
        if isinstance(entry, Mapping) and entry.get("key") == key:
            return entry
    return None


__all__ = ["PAGE_CACHE_SCHEMA_VERSION", "build_page_cache", "build_page_cache_entry", "find_cached_page"]
