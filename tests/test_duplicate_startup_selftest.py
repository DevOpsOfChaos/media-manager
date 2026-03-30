from __future__ import annotations

from media_manager.duplicate_startup_selftest import (
    ensure_duplicate_detection_startup_selftest,
    run_duplicate_detection_startup_selftest,
)


def test_duplicate_startup_selftest_passes_on_internal_dataset() -> None:
    result = run_duplicate_detection_startup_selftest()

    assert result.passed is True
    assert result.checks_run >= 10
    assert result.failures == []


def test_duplicate_startup_selftest_cached_entrypoint_returns_pass() -> None:
    result = ensure_duplicate_detection_startup_selftest()

    assert result.passed is True
    assert result.failures == []
