# Duplicate Workflow Diagnostics Hardening v2

## Goal

Make the exact-duplicate workflow easier to trust and debug when decisions come from a mix of
session restore and policy auto-selection.

## What is new

- decision summaries now distinguish between:
  - groups decided from a restored session
  - groups decided from the current policy
  - groups that remain undecided
- JSON reports now include unresolved cleanup groups with their candidate paths
- execution-preview JSON now includes grouped reason counters for executable, deferred, and blocked rows
- session-store coverage now verifies mismatch handling and normalization rules more explicitly

## Why this matters

The duplicate engine already finds groups and the workflow can already preview or apply delete actions.
The remaining friction in real use is often diagnostic:

- why were only some groups decided?
- did the session restore actually apply?
- which groups are still unresolved?
- why are rows blocked or deferred?

This block makes those answers visible without changing the actual duplicate matching rules.
