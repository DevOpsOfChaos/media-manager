from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import parse_qs, urlparse
from typing import Any

DEEP_LINK_SCHEMA_VERSION = "1.0"
ALLOWED_PAGES = {"dashboard", "new-run", "people-review", "run-history", "profiles", "settings", "execution"}
PAGE_ALIASES = {"people": "people-review", "runs": "run-history", "doctor": "settings"}


def normalize_deep_link_page(value: object) -> str:
    page = str(value or "dashboard").strip().lower().replace("_", "-")
    page = PAGE_ALIASES.get(page, page)
    return page if page in ALLOWED_PAGES else "dashboard"


def parse_qt_deep_link(value: str | Mapping[str, Any]) -> dict[str, object]:
    if isinstance(value, Mapping):
        page = normalize_deep_link_page(value.get("page") or value.get("active_page_id"))
        params = {str(key): str(raw) for key, raw in value.items() if raw is not None}
        return {"schema_version": DEEP_LINK_SCHEMA_VERSION, "kind": "qt_deep_link", "valid": True, "page_id": page, "params": params}

    text = str(value or "").strip()
    if not text:
        return {"schema_version": DEEP_LINK_SCHEMA_VERSION, "kind": "qt_deep_link", "valid": False, "page_id": "dashboard", "params": {}, "problem": "empty_link"}
    parsed = urlparse(text)
    if parsed.scheme and parsed.scheme not in {"media-manager", "media-manager-gui"}:
        return {"schema_version": DEEP_LINK_SCHEMA_VERSION, "kind": "qt_deep_link", "valid": False, "page_id": "dashboard", "params": {}, "problem": "unsupported_scheme"}
    query = parse_qs(parsed.query)
    page_hint = query.get("page", [parsed.netloc or parsed.path.strip("/") or "dashboard"])[0]
    params = {key: values[-1] for key, values in query.items() if values}
    return {"schema_version": DEEP_LINK_SCHEMA_VERSION, "kind": "qt_deep_link", "valid": True, "page_id": normalize_deep_link_page(page_hint), "params": params}


def deep_link_to_navigation_intent(link: Mapping[str, Any]) -> dict[str, object]:
    return {
        "kind": "navigation_intent",
        "page_id": normalize_deep_link_page(link.get("page_id")),
        "params": dict(link.get("params") if isinstance(link.get("params"), Mapping) else {}),
        "executes_immediately": False,
        "requires_confirmation": False,
    }


__all__ = ["ALLOWED_PAGES", "DEEP_LINK_SCHEMA_VERSION", "deep_link_to_navigation_intent", "normalize_deep_link_page", "parse_qt_deep_link"]
