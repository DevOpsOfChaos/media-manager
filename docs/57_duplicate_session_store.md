# Duplicate session store

This step adds a persistent snapshot format for exact-duplicate review decisions.

## Added module
- `src/media_manager/duplicate_session_store.py`

## Goal
The duplicate feature now has a small persistence layer that can store and restore exact-duplicate keep decisions in a deterministic way.

## Supported operations
- build a stable duplicate-group signature
- normalize decisions against the current exact groups
- save a snapshot to JSON
- load a snapshot from JSON
- restore decisions only when the current exact-group signature still matches

## Why this matters
The project already had:
- exact duplicate scan
- review decisions in memory
- dry-run planning
- execution preview
- execution runner
- orchestration module

But exact-duplicate review decisions still had no dedicated persistence layer of their own.

This module is the first clean building block for later:
- resume exact duplicate review
- preserve keep selections between app restarts
- reconnect saved decisions to later dry-run and execution stages

## Current safety behavior
If the current exact-group signature differs from the stored snapshot, restore returns an empty decision set instead of applying stale decisions.
