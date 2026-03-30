from __future__ import annotations

import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .duplicates import (
    DuplicateScanConfig,
    _build_exact_group,
    _group_by_size,
    _sample_offsets,
    compute_full_hash,
    compute_sample_fingerprint,
    files_are_identical,
    scan_exact_duplicates,
)


@dataclass(slots=True)
class DuplicateStartupSelfTestResult:
    passed: bool
    checks_run: int
    duration_ms: int
    failures: list[str] = field(default_factory=list)


_HAS_RUN = False
_LAST_RESULT: DuplicateStartupSelfTestResult | None = None


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _write_test_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def run_duplicate_detection_startup_selftest() -> DuplicateStartupSelfTestResult:
    started = time.perf_counter()
    failures: list[str] = []
    checks_run = 0

    try:
        small_offsets = _sample_offsets(1024, 512)
        checks_run += 1
        _assert(small_offsets == [0], "_sample_offsets should collapse small files to a single offset")

        large_offsets = _sample_offsets(4096, 512)
        checks_run += 1
        _assert(
            len(large_offsets) == 3 and large_offsets[0] == 0 and len(set(large_offsets)) == 3,
            "_sample_offsets should return 3 unique offsets for larger files",
        )

        with tempfile.TemporaryDirectory(prefix="media_manager_dup_selftest_") as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)

            duplicate_payload = (b"HEADER" * 20000) + (b"MIDDLE" * 20000) + (b"FOOTER" * 20000)
            different_same_size_payload = b"X" * len(duplicate_payload)
            unique_payload = b"UNIQUE" * 7000

            duplicate_a = tmp_dir / "camera_a" / "IMG_0001.JPG"
            duplicate_b = tmp_dir / "camera_b" / "IMG_0001.JPG"
            duplicate_c = tmp_dir / "camera_c" / "IMG_0002.JPG"
            same_size_other = tmp_dir / "camera_d" / "VIDEO_0001.MP4"
            same_size_other_2 = tmp_dir / "camera_e" / "VIDEO_0002.MP4"
            ignored_text = tmp_dir / "notes" / "readme.txt"

            _write_test_bytes(duplicate_a, duplicate_payload)
            _write_test_bytes(duplicate_b, duplicate_payload)
            _write_test_bytes(duplicate_c, duplicate_payload)
            _write_test_bytes(same_size_other, different_same_size_payload)
            _write_test_bytes(same_size_other_2, unique_payload.ljust(len(duplicate_payload), b"Z"))
            _write_test_bytes(ignored_text, duplicate_payload)

            sample_a = compute_sample_fingerprint(duplicate_a)
            sample_b = compute_sample_fingerprint(duplicate_b)
            sample_other = compute_sample_fingerprint(same_size_other)
            checks_run += 1
            _assert(sample_a == sample_b, "compute_sample_fingerprint should match for identical files")
            checks_run += 1
            _assert(sample_a != sample_other, "compute_sample_fingerprint should differ for different content")

            full_a = compute_full_hash(duplicate_a)
            full_b = compute_full_hash(duplicate_b)
            full_other = compute_full_hash(same_size_other)
            checks_run += 1
            _assert(full_a == full_b, "compute_full_hash should match for identical files")
            checks_run += 1
            _assert(full_a != full_other, "compute_full_hash should differ for different content")

            checks_run += 1
            _assert(files_are_identical(duplicate_a, duplicate_b), "files_are_identical should return True for identical files")
            checks_run += 1
            _assert(
                not files_are_identical(duplicate_a, same_size_other),
                "files_are_identical should return False for different files of same size",
            )

            grouped = _group_by_size([duplicate_a, duplicate_b, duplicate_c, same_size_other, same_size_other_2])
            checks_run += 1
            _assert(len(grouped[len(duplicate_payload)]) == 5, "_group_by_size should group all same-size test files together")

            exact_group = _build_exact_group([duplicate_c, duplicate_a, duplicate_b], len(duplicate_payload), sample_a, full_a)
            checks_run += 1
            _assert(exact_group.files[0].name == "IMG_0001.JPG", "_build_exact_group should sort paths deterministically")
            checks_run += 1
            _assert(
                not exact_group.same_name and exact_group.same_suffix,
                "_build_exact_group should report same_name/same_suffix correctly",
            )

            progress_messages: list[str] = []
            scan_result = scan_exact_duplicates(
                DuplicateScanConfig(source_dirs=[tmp_dir]),
                progress_callback=progress_messages.append,
            )

            checks_run += 1
            _assert(scan_result.scanned_files == 5, "scan_exact_duplicates should scan only media files from the self-test dataset")
            checks_run += 1
            _assert(
                len(scan_result.exact_groups) == 1,
                "scan_exact_duplicates should find exactly one exact duplicate group in the self-test dataset",
            )
            checks_run += 1
            _assert(
                scan_result.exact_duplicate_files == 3 and scan_result.exact_duplicates == 2,
                "scan_exact_duplicates should count duplicate files and extras correctly",
            )
            checks_run += 1
            _assert(scan_result.errors == 0, "scan_exact_duplicates self-test should complete without errors")

            detected_group = scan_result.exact_groups[0]
            checks_run += 1
            _assert(
                not detected_group.same_name and detected_group.same_suffix,
                "scan_exact_duplicates should preserve same_name/same_suffix metadata",
            )
            checks_run += 1
            _assert(
                any(message.startswith("Stage 1/4") for message in progress_messages)
                and any(message.startswith("Stage 2/4") for message in progress_messages)
                and any(message.startswith("Stage 3/4") for message in progress_messages)
                and any(message.startswith("Stage 4/4") for message in progress_messages)
                and any(message.startswith("Finished.") for message in progress_messages),
                "scan_exact_duplicates should emit all expected progress stages during the self-test",
            )

    except Exception as exc:
        failures.append(str(exc))

    duration_ms = int((time.perf_counter() - started) * 1000)
    return DuplicateStartupSelfTestResult(
        passed=len(failures) == 0,
        checks_run=checks_run,
        duration_ms=duration_ms,
        failures=failures,
    )


def ensure_duplicate_detection_startup_selftest() -> DuplicateStartupSelfTestResult:
    global _HAS_RUN, _LAST_RESULT

    if os.environ.get("MEDIA_MANAGER_DISABLE_DUPLICATE_SELFTEST", "0") == "1":
        result = DuplicateStartupSelfTestResult(
            passed=True,
            checks_run=0,
            duration_ms=0,
            failures=[],
        )
        _HAS_RUN = True
        _LAST_RESULT = result
        return result

    if _HAS_RUN and _LAST_RESULT is not None:
        return _LAST_RESULT

    result = run_duplicate_detection_startup_selftest()
    _HAS_RUN = True
    _LAST_RESULT = result

    if result.passed:
        print(
            f"[duplicate-selftest] PASS {result.checks_run} check(s) in {result.duration_ms} ms",
            flush=True,
        )
        return result

    failure_message = " | ".join(result.failures) if result.failures else "unknown failure"

    if os.environ.get("MEDIA_MANAGER_ALLOW_DUPLICATE_SELFTEST_FAILURE", "0") == "1":
        print(f"[duplicate-selftest] FAIL {failure_message}", flush=True)
        return result

    raise RuntimeError(f"Duplicate detection startup self-test failed: {failure_message}")
