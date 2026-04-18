# Metadata / Inspect / ExifTool Hardening v1

This block tightens the metadata inspection path without widening the project scope.

## What changed

- ExifTool path resolution is more forgiving:
  - explicit file paths still work
  - explicit directory paths are now searched for common executable names
  - `EXIFTOOL_PATH` can point to either a file or a directory
- ExifTool execution now reports clearer error kinds:
  - `not_found`
  - `timeout`
  - `command_error`
  - `invalid_json`
- File inspection now records:
  - metadata tag count
  - metadata error kind
  - date candidate count indirectly via the candidate list
- `media-manager inspect --json` now returns:
  - a top-level summary by chosen source kind
  - per-file metadata diagnostics

## Why this matters

The date resolver and organize / rename flows depend on metadata inspection.
That means weak observability in the inspect layer becomes debugging pain everywhere else.
This block improves that observability while staying CLI-first and GUI-friendly.

## Notes

This still does not introduce any long-running ExifTool session handling.
The goal here is better diagnostics and a sturdier one-shot CLI path.
