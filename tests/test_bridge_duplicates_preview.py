"""Tests for bridge_duplicates_preview — read-only duplicate scan only."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from media_manager.bridge_duplicates_preview import cmd_preview, main


def _parse_final_output(stdout_text: str) -> dict:
    """Parse the final JSON result from stdout, skipping any early-group lines."""
    for line in stdout_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "kind" in parsed:
            return parsed
    raise ValueError("No final result found in stdout")


def _parse_early_groups(stdout_text: str) -> list[dict]:
    """Parse early-group JSON lines from stdout."""
    groups = []
    for line in stdout_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "files" in parsed and "file_size" in parsed and "kind" not in parsed:
            groups.append(parsed)
    return groups


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


def test_preview_emits_early_groups_on_stdout(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "dup1.jpg").write_bytes(b"same-content")
    (source / "dup2.jpg").write_bytes(b"same-content")

    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = StringIO(json.dumps({"source_dirs": [str(source)]}))
    sys.stdout = StringIO()
    try:
        exit_code = cmd_preview()
        assert exit_code == 0
        stdout_text = sys.stdout.getvalue()

        early = _parse_early_groups(stdout_text)
        assert len(early) >= 1, f"Expected early groups, got: {stdout_text}"
        for g in early:
            assert len(g["files"]) >= 2
            assert g["file_size"] > 0

        final = _parse_final_output(stdout_text)
        assert final["kind"] == "preview"
        assert final["exact_groups"][0]["full_digest"] == early[0]["full_digest"]
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


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
        output = _parse_final_output(sys.stdout.getvalue())
        assert output["kind"] == "preview"
        assert output["scanned_files"] >= 2
        assert len(output["exact_groups"]) >= 1
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
        output = _parse_final_output(sys.stdout.getvalue())
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
        output = _parse_final_output(sys.stdout.getvalue())
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
