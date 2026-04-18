# Date / Metadata Decision Policy Hardening v3

This block makes date resolution easier to inspect and reason about.

## What changed

- `DateResolution` now carries lightweight policy diagnostics:
  - parseable candidate count
  - unparseable candidate count
  - metadata conflict flag
  - decision policy label
- metadata decisions now distinguish between:
  - multiple parseable candidates that agree
  - multiple parseable candidates that disagree
- `media-manager inspect` surfaces these diagnostics in both JSON and text output.

## Why this helps

The CLI can now explain not only which date was chosen, but also whether the metadata was internally consistent or whether the resolver had to pick one candidate among conflicting parseable values.
