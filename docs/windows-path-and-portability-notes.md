# Windows path and portability notes

The project is intentionally Windows-first right now, which means path behavior is not a secondary concern.

Several workflow/profile/history regressions were caused by treating path values inconsistently across:

- in-memory `Path` objects
- JSON payloads
- bundle relative paths
- `contains` filters
- text output

This document summarizes the practical rules that help avoid those breaks.

## Rule 1: JSON should prefer stable text, not raw `Path` objects

If a JSON payload leaves the process boundary, normalize it into plain strings.

That especially applies to:

- `path`
- `entry_path`
- `profile_path`
- `latest_path`
- target paths in bundle extract/sync results

Why:

- regression tests often use string operations like `.endswith(...)`
- callers may serialize/compare exact JSON payloads
- keeping raw `Path` objects in model helpers increases accidental type drift

## Rule 2: portable bundle paths should use `/`

Bundle-internal relative paths are not the same as local OS paths.

For bundle JSON and related comparisons, use forward-slash style:

- `family/cleanup.json`
- `trips/italy.json`

Why:

- bundle files are a portable exchange format
- Windows backslashes create avoidable comparison noise
- tests often rely on a single canonical relative path form

## Rule 3: `contains` filters should normalize both sides

For filters like:

- `--profile-path-contains`
- `--relative-path-contains`

normalize both the source path and the search text before comparing.

Practical expectation:

- `family/`
- `family\`

should both match the same Windows profile path when the logical path segment is the same.

## Rule 4: keep root path and entry path separate in history JSON

For `workflow last --json`, it is useful to distinguish:

- history root path: the directory that was scanned
- entry path: the concrete matching file

Do not silently overload one field for both purposes.

Current compatibility-sensitive pattern:

- `path` = root scan path
- `entry_path` = concrete file path
- nested `entry.path` = concrete file path

## Rule 5: be careful when changing dataclass field types

If a field is used in tests or downstream payload building, switching from:

- `str` to `Path`
- `Path` to `str`

can break behavior even if the information content is identical.

Examples:

- `.endswith(...)` works on strings, not `Path`
- JSON dumps are simpler when the field is already a string

When in doubt, keep the in-memory field type aligned with the strongest existing regression contract.

## Rule 6: respect existing summary semantics

Some summary values are compatibility-sensitive even if a newer alternative might appear more intuitive.

Example:

- `build_history_summary(...)["latest_created_at_utc"]`

may be expected to come from the first input entry rather than recomputing the true newest timestamp.

Do not “fix” such behavior casually unless you also update the full compatibility surface intentionally.

## Safe implementation checklist

Before shipping a path-related change, check:

1. Are JSON fields plain strings where callers expect strings?
2. Are bundle relative paths still forward-slash canonical?
3. Do slash and backslash filter variants both work?
4. Did any existing test rely on string methods like `.endswith(...)`?
5. Did any text output or summary field change meaning unintentionally?
6. Was the full `pytest -q` run, not only the new focused tests?
