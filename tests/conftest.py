"""Shared pytest fixtures for media-manager tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def temp_media_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample media files."""
    source = tmp_path / "photos"
    source.mkdir()
    for i in range(5):
        (source / f"IMG_{i:04d}.jpg").write_bytes(b"fake-jpeg-data")
    (source / "video.mp4").write_bytes(b"fake-mp4-data")
    (source / "sidecar.xmp").write_bytes(b"<xmp></xmp>")
    return source


@pytest.fixture
def temp_empty_dir(tmp_path: Path) -> Path:
    """Create an empty temporary directory."""
    d = tmp_path / "empty"
    d.mkdir()
    return d


@pytest.fixture
def temp_catalog_file(tmp_path: Path) -> Path:
    """Create a minimal people catalog JSON file."""
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({
        "schema_version": 1,
        "persons": {},
    }))
    return catalog


@pytest.fixture
def temp_settings_file(tmp_path: Path) -> Path:
    """Create a minimal GUI settings JSON file."""
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({
        "language": "en",
        "theme": "system",
        "density": "comfortable",
        "source_dirs": [],
    }))
    return settings


@pytest.fixture
def temp_journal_file(tmp_path: Path) -> Path:
    """Create a minimal execution journal JSON file."""
    journal = tmp_path / "journal.json"
    journal.write_text(json.dumps({
        "schema_version": 1,
        "journal_type": "organize",
        "entries": [],
        "run_id": "test-run",
        "created_at": "2024-01-01T00:00:00Z",
    }))
    return journal
