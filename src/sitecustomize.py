from __future__ import annotations

try:
    from media_manager.duplicate_startup_selftest import ensure_duplicate_detection_startup_selftest
except Exception as exc:  # pragma: no cover - startup safeguard
    raise RuntimeError(f"Failed to import duplicate startup self-test: {exc}") from exc

ensure_duplicate_detection_startup_selftest()
