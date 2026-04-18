# Organize/Rename/Inspect Reporting Hardening v2

This block improves CLI diagnostics without changing the underlying workflow scope.

## What is improved

- `media-manager organize --json` now includes plan and execution summaries:
  - status summary
  - reason summary
  - resolution source summary
  - confidence summary
  - execution outcome summary
- `media-manager rename --json` now includes the same style of dry-run summaries,
  plus execution status/action summaries.
- `media-manager inspect` now reports richer diagnostic summaries:
  - total files
  - metadata and ExifTool availability counts
  - warning count
  - source kind summary
  - confidence summary
  - timezone summary
  - metadata error summary
  - parseable vs unparseable candidate counts

## Why it matters

The CLI is becoming easier to trust on real-world batches because it explains not only
what it decided, but also how often those decision paths occurred.
