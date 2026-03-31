# Stale preflight protection for duplicate execution

This step adds a preflight revalidation layer before exact-duplicate delete preview or apply continues.

## Changed module
- `src/media_manager/execution_runner.py`

## New checks
Before a delete row is previewed or sent to trash, the runner now verifies:
- the source file still exists
- the source file size still matches the size captured during scan
- the survivor path is still present in the execution row
- the survivor file still exists on disk
- the source file still matches the survivor byte-for-byte
- no same-stem associated siblings are present

## Why this matters
The execution path already had:
- sidecar protection
- trash-based deletion

But it still trusted the earlier duplicate scan too much.
If files changed on disk after the scan, the runner could otherwise execute based on stale assumptions.

## Effect
Potentially stale delete rows are now blocked with explicit reasons such as:
- `source_size_changed_since_scan`
- `survivor_missing_on_disk`
- `source_no_longer_matches_survivor`

This makes the duplicate execution path substantially harder to misuse after the file system changed between scan and execution.
