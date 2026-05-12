"""Tests for bridge_duplicates_preview — read-only duplicate scan only."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from media_manager.bridge_duplicates_preview import cmd_preview, main


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
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"same-content")
    (source / "b.jpg").write_bytes(b"same-content")

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        assert output["scanned_files"] >= 2
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_never_modifies_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "dup1.jpg").write_bytes(b"duplicate-data")
    (source / "dup2.jpg").write_bytes(b"duplicate-data")

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        cmd_preview()
        # Files must remain untouched
        assert (source / "dup1.jpg").read_bytes() == b"duplicate-data"
        assert (source / "dup2.jpg").read_bytes() == b"duplicate-data"
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_no_duplicates_empty_groups(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "unique.jpg").write_bytes(b"unique-a")
    (source / "other.jpg").write_bytes(b"unique-b")

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert len(output["exact_groups"]) == 0
        assert output["exact_duplicates"] == 0
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_preview_nonexistent_source(tmp_path: Path) -> None:
    source = tmp_path / "does_not_exist"

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        output = json.loads(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        assert output["scanned_files"] == 0
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def test_main_returns_exit_code(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"aa")

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
