from __future__ import annotations

import os
import re
from pathlib import Path

from media_manager.core.date_resolver import DateResolution

INVALID_FILENAME_CHARS = '<>:"/\\|?*'
_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)(?::([^{}]+))?\}")


def sanitize_filename(value: str) -> str:
    cleaned = value.strip()
    for char in INVALID_FILENAME_CHARS:
        cleaned = cleaned.replace(char, "_")
    cleaned = cleaned.replace("\n", "_").replace("\r", "_")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(" .")


def render_rename_filename(file_path: Path, resolution: DateResolution, template: str, *, index: int, source_root: Path | None = None) -> str:
    dt = resolution.resolved_datetime

    def replace(match: re.Match[str]) -> str:
        token_name = match.group(1)
        token_format = match.group(2)
        if token_name in {"date", "datetime"}:
            fmt = token_format or "%Y-%m-%d_%H-%M-%S"
            return dt.strftime(fmt)
        if token_name == "year": return dt.strftime("%Y")
        if token_name == "month": return dt.strftime("%m")
        if token_name == "day": return dt.strftime("%d")
        if token_name == "hour": return dt.strftime("%H")
        if token_name == "minute": return dt.strftime("%M")
        if token_name == "second": return dt.strftime("%S")
        if token_name == "year_month": return dt.strftime("%Y-%m")
        if token_name == "year_month_day": return dt.strftime("%Y-%m-%d")
        if token_name == "stem": return sanitize_filename(file_path.stem)
        if token_name == "suffix": return file_path.suffix
        if token_name == "source_name": return sanitize_filename(source_root.name if source_root is not None else "")
        if token_name == "index": return f"{index:04d}"
        raise ValueError(f"Unknown rename template token: {token_name}")

    rendered = _PLACEHOLDER_RE.sub(replace, template)
    if "{" in rendered or "}" in rendered:
        raise ValueError("Rename template contains unmatched braces or unsupported placeholders.")
    includes_suffix = "{suffix}" in template
    cleaned = sanitize_filename(rendered)
    if not cleaned:
        raise ValueError("Rename template produced an empty file name.")
    base_name = cleaned if includes_suffix else cleaned + file_path.suffix
    final_name = sanitize_filename(base_name)
    if not final_name:
        raise ValueError("Rename template produced an invalid file name.")
    root, ext = os.path.splitext(final_name)
    if not root:
        raise ValueError("Rename template produced a file name without a valid stem.")
    if not ext:
        final_name = root + file_path.suffix
    return final_name
