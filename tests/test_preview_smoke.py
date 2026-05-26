"""Smoke tests for organize preview pipeline."""
from pathlib import Path
import tempfile
import json
import sys
import io

sys.path.insert(0, "D:/LocalRepos/media-manager/src")

from media_manager.bridge_organize_preview import cmd_preview


def _run_preview(payload: dict) -> tuple[int, str]:
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO(json.dumps(payload))
    sys.stdout = io.StringIO()
    try:
        exit_code = cmd_preview()
        output = sys.stdout.getvalue()
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout
    return exit_code, output


def test_step1_copy_mode():
    """STEP 1: Test with copy mode."""
    tmp = Path(tempfile.mkdtemp())
    try:
        source = tmp / "source"
        source.mkdir()
        target = tmp / "organized"
        target.mkdir()
        (source / "photo1.jpg").write_bytes(b"fake jpg data")
        (source / "photo2.png").write_bytes(b"fake png data")
        (source / "video1.mp4").write_bytes(b"fake mp4 data")

        payload = {
            "source_dirs": [str(source)],
            "target_root": str(target),
            "pattern": "{year}/{year_month_day}",
            "recursive": True,
            "include_hidden": False,
            "follow_symlinks": False,
            "operation_mode": "copy",
            "include_associated_files": False,
            "conflict_policy": "conflict",
            "include_patterns": [],
            "exclude_patterns": [],
            "batch_size": 0,
        }

        exit_code, output = _run_preview(payload)
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}: {output}"
        result = json.loads(output)
        assert result.get("kind") == "preview"
        assert result.get("dry_run") is True
        assert result["planned_count"] == 3
        assert result["entries"][0]["operation_mode"] == "copy"
        print("STEP 1 PASS: copy mode works correctly")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_step2_link_mode():
    """STEP 2: Test with link mode."""
    tmp = Path(tempfile.mkdtemp())
    try:
        source = tmp / "source"
        source.mkdir()
        target = tmp / "organized"
        target.mkdir()
        (source / "photo1.jpg").write_bytes(b"fake jpg data")

        payload = {
            "source_dirs": [str(source)],
            "target_root": str(target),
            "pattern": "{year}/{year_month_day}",
            "operation_mode": "link",
        }

        exit_code, output = _run_preview(payload)
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}: {output}"
        result = json.loads(output)
        assert result["planned_count"] >= 1
        assert result["entries"][0]["operation_mode"] == "link"
        print("STEP 2 PASS: link mode works correctly")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def test_step3_nonexistent_source():
    """STEP 3: Test with nonexistent source directory."""
    tmp = Path(tempfile.mkdtemp())
    try:
        target = tmp / "organized"
        target.mkdir()
        nonexistent = tmp / "nope"

        payload = {
            "source_dirs": [str(nonexistent)],
            "target_root": str(target),
            "pattern": "{year}/{year_month_day}",
        }

        exit_code, output = _run_preview(payload)
        # Should return error because no valid source dirs were found
        assert exit_code != 0, f"Expected error exit code, got {exit_code}: {output}"
        print(f"STEP 3 PASS: nonexistent source returns error (exit={exit_code})")
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_step1_copy_mode()
    test_step2_link_mode()
    test_step3_nonexistent_source()
    print("ALL SMOKE TESTS PASSED")
