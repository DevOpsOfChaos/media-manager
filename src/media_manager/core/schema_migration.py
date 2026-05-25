"""Schema migration for persisted data models."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def migrate_catalog(data: dict[str, Any], target_version: int = 1) -> dict[str, Any]:
    """Migrate a people catalog to the target schema version."""
    current = int(data.get("schema_version", 0))
    while current < target_version:
        _migrate_catalog_step(data, current, current + 1)
        current += 1
    return data


def migrate_journal(data: dict[str, Any], target_version: int = 1) -> dict[str, Any]:
    """Migrate an execution journal to the target schema version."""
    current = int(data.get("schema_version", 0))
    while current < target_version:
        _migrate_journal_step(data, current, current + 1)
        current += 1
    return data


def migrate_settings(data: dict[str, Any], target_version: int = 1) -> dict[str, Any]:
    """Migrate GUI settings to the target schema version."""
    raw = data.get("schema_version", "0")
    current = int(float(str(raw))) if raw else 0
    while current < target_version:
        _migrate_settings_step(data, current, current + 1)
        current += 1
    return data


def _migrate_catalog_step(data: dict[str, Any], from_ver: int, to_ver: int) -> None:
    """Apply a single catalog migration step."""
    if from_ver == 0 and to_ver == 1:
        # v0 -> v1: ensure all persons have an "aliases" field
        for person in data.get("persons", {}).values():
            person.setdefault("aliases", [])
            person.setdefault("notes", "")
    data["schema_version"] = to_ver
    logger.info("Migrated catalog from schema v%s to v%s", from_ver, to_ver)


def _migrate_journal_step(data: dict[str, Any], from_ver: int, to_ver: int) -> None:
    """Apply a single journal migration step."""
    data["schema_version"] = to_ver
    logger.info("Migrated journal from schema v%s to v%s", from_ver, to_ver)


def _migrate_settings_step(data: dict[str, Any], from_ver: int, to_ver: int) -> None:
    """Apply a single settings migration step."""
    data["schema_version"] = str(to_ver)
    logger.info("Migrated settings from schema v%s to v%s", from_ver, to_ver)


def load_with_migration(path: Path, migrate_fn, target_version: int = 1) -> dict[str, Any]:
    """Load a JSON file and migrate to target schema version."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return migrate_fn(raw, target_version)
