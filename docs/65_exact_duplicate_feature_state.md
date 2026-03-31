# Exact duplicate feature state

This document describes the current state of the exact-duplicate path.

## What already exists

### Detection
- exact duplicate detection via hashing and byte identity
- startup self-test for the duplicate engine
- automated regression coverage for duplicate helpers and scans

### Review and planning
- exact-duplicate review foundation in the workflow shell
- exact-duplicate cleanup-plan model
- exact-duplicate dry-run model
- exact-duplicate execution-preview model
- exact-duplicate session snapshot persistence

### Execution and safety
- exact-duplicate execution runner baseline
- trash-based delete execution
- associated-file detection foundation
- associated-file safety blocking in the delete path
- stale preflight blocking when files changed since scan
- structured execution audit logging
- CLI exit codes that distinguish success, errors, and incomplete apply runs

### Interfaces
- `media-manager-duplicates` CLI
- backend orchestration module for exact-duplicate workflows
- partial QML workflow integration

## What does not exist yet

### Missing decision model depth
The current exact-duplicate path still lacks rich action choices such as:
- keep-source
- keep-target
- keep-both
- larger batch queue management

Right now the backend is much stronger than the final user-facing decision UX.

### Missing GUI execution surface
There is still no final full-page GUI surface for:
- dry-run rows
- execution-preview rows
- blocked/deferred explanations
- real apply controls with strong status feedback

This is one of the biggest visible product gaps.

### Missing likely-duplicate handling
The current path is for exact duplicates only.
Similarity review and comparison UX are still future work.

### Missing associated-file execution semantics
The system can currently detect and block dangerous delete situations when associated files exist.
That is a safety baseline, not a final associated-file handling model.

It still needs real semantics for questions like:
- move both together
- rename both together
- keep RAW+JPEG together
- preserve XMP/AAE/SRT relationships during execution

## Current truth in one sentence
The exact-duplicate path is no longer a toy.
It has real backend depth, safety layers, auditability, and CLI usability.
The main remaining weakness is the incomplete final GUI surface and decision UX.

## Recommended next steps
1. Surface duplicate dry-run and execution-preview rows in the QML workflow
2. Add richer duplicate decision actions beyond the current keep-candidate baseline
3. Turn associated-file blocking into explicit handling choices
4. Add final user-facing apply controls with clear result reporting
