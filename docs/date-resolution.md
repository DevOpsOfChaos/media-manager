# Date Resolution v1

## Goal

Resolve one practical capture datetime for a media file in a way that is:

- explainable
- testable
- safe to improve later

This is intentionally not the final resolver.

## Current order

The current resolver works in this order:

1. parseable metadata candidates from ExifTool inspection
2. recognized filename patterns
3. filesystem modification time (`mtime`)

## Confidence levels

### High
Used when a parseable metadata candidate wins.

### Medium
Used when metadata was missing or unusable, but a recognized filename pattern could be parsed.

### Low
Used when both metadata and filename parsing fail and the resolver must fall back to `mtime`.

## Current limitations

- no timezone correction policy yet
- no location or trip context yet
- no camera-specific overrides yet
- no multi-tag conflict scoring beyond first parseable metadata candidate

## Why this is still useful

It gives the project a stable baseline that can be debugged through `media-manager inspect` and improved incrementally instead of hiding date selection inside fragile one-off heuristics.
