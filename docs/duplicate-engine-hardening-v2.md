# Duplicate Engine Hardening v2

## Goal

Make the exact-duplicate scan more robust when individual files fail during one stage of the pipeline.

## What changed

The duplicate scanner now keeps running when a single file fails during:

- size grouping
- sample fingerprinting
- full hashing
- final byte comparison

Instead of collapsing all failures into one opaque error counter, the scan now records:

- `size_group_errors`
- `sample_errors`
- `hash_errors`
- `compare_errors`

The existing `errors` field still remains as the total error count for compatibility.

## Why this matters

Large real-world libraries often contain:

- half-synced files
- locked files
- temporarily unavailable files
- files that disappear during scanning

With this change, one bad file is less likely to hide useful duplicate results for the rest of the library.
