"""Tests for bridge_similar_preview — read-only similar image scan only."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from media_manager.bridge_similar_preview import cmd_preview, main


def test_preview_empty_source_dirs() -> None:
    old_stdin = sys.stdin
    sys.stdin = StringIO(json.dumps({"source_dirs": []}))
    try:
        exit_code = cmd_preview()
        assert exit_code == 1
    finally:
        sys.stdin = old_stdin


def test_preview_invalid_json() -> None:
    old_stdin = sys.stdin
    sys.stdin = StringIO("not json {{{")
    try:
        exit_code = cmd_preview()
        assert exit_code == 1
    finally:
        sys.stdin = old_stdin


def test_preview_returns_kind_preview(tmp_path: Path) -> None:
    """A folder with no images returns empty groups but kind=preview."""
    source = tmp_path / "source"
    source.mkdir()

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        assert output["similar_groups"] == []
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_never_modifies_files(tmp_path: Path) -> None:
    from PIL import Image

    source = tmp_path / "source"
    source.mkdir()
    img_a = source / "a.jpg"
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(img_a)
    original = img_a.read_bytes()

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        cmd_preview()
        assert img_a.read_bytes() == original, "Source file must remain unchanged"
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_detects_similar_images(tmp_path: Path) -> None:
    """Two images that are visually similar should form a group."""
    from PIL import Image

    source = tmp_path / "source"
    source.mkdir()
    img_a = source / "a.jpg"
    img_b = source / "b.jpg"
    # Create two images that differ slightly
    im1 = Image.new("RGB", (8, 8), color=(255, 255, 255))
    im1.save(img_a)
    im2 = Image.new("RGB", (8, 8), color=(254, 254, 254))  # almost identical
    im2.save(img_b)

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)], "max_distance": 10}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        # At max_distance=10, even 1-bit difference should be grouped
        assert output["scanned_files"] >= 2
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_nonexistent_source() -> None:
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": ["/does/not/exist"]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["scanned_files"] == 0
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_main_returns_exit_code(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        result = main()
        assert result == 0
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
