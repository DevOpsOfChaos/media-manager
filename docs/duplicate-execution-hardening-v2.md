# Duplicate Execution Hardening v2

This block improves the execution side of the duplicate workflow without widening scope.

## Goal

Make the duplicate delete path safer and easier to audit when a review decision becomes stale between scan time and apply time.

## What changed

- execution results now expose more specific counters:
  - `previewed_rows`
  - `deleted_rows`
  - `blocked_associated_rows`
  - `blocked_missing_survivor_rows`
- delete execution now blocks when the recommended keep file is missing at execution time
- JSON reports now include the extra execution counters

## Why this matters

A duplicate decision can be valid at scan time and stale at apply time.
If the planned survivor disappears before execution, deleting the other file becomes unsafe.
This block turns that situation into a blocked result instead of blindly continuing.

## Current scope

This still only hardens the exact-duplicate execution path.
It does not add copy/move execution for duplicate cleanup yet.
