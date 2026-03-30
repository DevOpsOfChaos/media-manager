# Duplicate detection startup self-test

This step adds an automatic startup self-test for the exact-duplicate engine.

## Goal
The app should verify the duplicate-detection core on every startup with a fast temporary dry run instead of trusting the code path blindly.

## Added files
- `src/media_manager/duplicate_startup_selftest.py`
- `src/sitecustomize.py`

## What is tested
The startup self-test currently exercises these duplicate-detection functions against a temporary media dataset:
- `_sample_offsets`
- `compute_sample_fingerprint`
- `compute_full_hash`
- `files_are_identical`
- `_group_by_size`
- `_build_exact_group`
- `scan_exact_duplicates`

## Dataset behavior
The self-test creates temporary media files only.
It does **not** scan the user’s real source folders.

## Startup behavior
- On success, startup prints a PASS line to stdout.
- On failure, startup raises a `RuntimeError` and stops.

## Escape hatches
- `MEDIA_MANAGER_DISABLE_DUPLICATE_SELFTEST=1` skips the startup self-test.
- `MEDIA_MANAGER_ALLOW_DUPLICATE_SELFTEST_FAILURE=1` allows startup to continue after a failed self-test while still printing the failure.

## Why `sitecustomize.py`
The project runs from Python, and `src/sitecustomize.py` gives a minimal startup hook without patching the existing workflow or duplicate UI state first.
