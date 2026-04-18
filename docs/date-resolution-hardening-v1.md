# Date resolution hardening v1

This block improves the rebuilt date-resolution layer without pulling GUI work forward.

## What improved

- broader datetime parsing support for common metadata shapes
- support for date-only metadata values
- support for `Z` timezone suffixes
- stronger filename fallback coverage for common real-world names
- clearer reasoning when lower-priority metadata candidates are ignored
- clearer fallback reasoning when metadata was present but unusable

## New filename cases

The resolver now understands more practical filename styles such as:

- `IMG_20240102_123456.jpg`
- `PXL_20240102_123456789.jpg`
- `WhatsApp Image 2024-01-02 at 12.34.56.jpeg`
- `Screenshot_2024-01-02-12-34-56.png`

## Why this matters

A stronger date resolver improves multiple CLI surfaces at once:

- inspect
- organize
- rename
- trip-oriented workflows

This keeps the architecture in the right order:

1. strengthen the core decision layer
2. expose it through CLI tools
3. keep later GUI work thin and dependent on the hardened backend
