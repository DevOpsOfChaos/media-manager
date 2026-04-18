from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.state import build_command_run_log, write_command_run_log


def test_build_command_run_log_contains_expected_fields() -> None:
    payload = {"planned_count": 3}
    result = build_command_run_log(
        command_name="organize",
        apply_requested=False,
        exit_code=0,
        payload=payload,
    )

    assert result["schema_version"] == 1
    assert result["command_name"] == "organize"
    assert result["apply_requested"] is False
    assert result["exit_code"] == 0
    assert result["payload"] == payload
    assert "created_at_utc" in result


def test_build_command_run_log_accepts_explicit_created_at() -> None:
    result = build_command_run_log(
        command_name="rename",
        apply_requested=True,
        exit_code=1,
        payload={"error_count": 2},
        created_at_utc="2026-04-18T10:11:12+00:00",
    )

    assert result["created_at_utc"] == "2026-04-18T10:11:12+00:00"


def test_write_command_run_log_roundtrip(tmp_path: Path) -> None:
    log_path = tmp_path / "logs" / "run-log.json"

    written = write_command_run_log(
        log_path,
        command_name="rename",
        apply_requested=True,
        exit_code=1,
        payload={"error_count": 2},
    )

    assert written == log_path
    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert payload["command_name"] == "rename"
    assert payload["apply_requested"] is True
    assert payload["exit_code"] == 1
    assert payload["payload"]["error_count"] == 2
