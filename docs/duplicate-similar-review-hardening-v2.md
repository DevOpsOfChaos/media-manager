# Duplicate / Similar Review Hardening v2

This block improves the review layer around visually similar images without pretending the underlying match is exact.

## What changed

- similar-review rows now carry a `match_kind`
- similar-review rows now carry a `review_priority`
- review candidates are ordered by distance to the recommended keep file
- JSON reports now expose priority counters for faster downstream inspection

## Match kinds

- `exact-hash` — the perceptual hash matches the keep candidate exactly
- `very-close` — distance 1 to 2
- `close` — distance 3 to 5
- `broad` — distance 6 or greater

## Review priority

- `high` for distances 0 to 2
- `medium` for distances 3 to 5
- `low` for distances 6 and above

These are still review signals, not deletion truth. Similar-image output remains guidance that a human can audit before removal.
