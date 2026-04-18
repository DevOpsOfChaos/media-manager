# Duplicate Reporting and Session Diagnostics v1

## Goal

Make duplicate runs easier to trust and easier to debug without changing the exact-duplicate core algorithm.

## What this block adds

- stage-level duplicate scan errors in JSON reports
- visible session-restore status in JSON reports
- visible session-restore status in CLI output
- merge behavior where restored decisions stay authoritative and policy-based auto decisions only fill remaining gaps

## Why this matters

A duplicate run can now answer two practical questions more clearly:

1. did the scan hit errors, and at which stage?
2. did the saved review session actually apply to the current duplicate set?

## Current scope

This block improves reporting and diagnostics only.
It does not change duplicate matching semantics.
