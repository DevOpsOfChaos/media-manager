# Implementation Block 1: Media Groups and Leftover Consolidation

This file narrows the V1 design into the first concrete implementation block.

It is intentionally conservative.

## Purpose of block 1

Block 1 should deliver real user value without trying to redesign the full repository at once.

Block 1 focuses on:

1. explicit media-group detection
2. organize execution support for media groups
3. rename execution support for media groups
4. cleanup workflow reporting/support for those grouped operations
5. optional leftover consolidation after apply-runs
6. journal/undo support for all grouped moves and leftover moves

## Out of scope for block 1

Not part of block 1:

- duplicates-specific review UX changes
- profile-bundle UX changes
- fuzzy or cross-directory associations
- advanced review buckets
- exact GUI/application service layer implementation

## Exact file associations included in block 1

### Associated sidecars

Allowed associated sidecar extensions:

- `.xmp`
- `.aae`

### RAW + JPEG sibling pairs

Allowed RAW extensions in block 1:

- `.dng`
- `.raw`
- `.arw`
- `.cr2`
- `.cr3`
- `.nef`
- `.orf`
- `.rw2`

Allowed JPEG sibling extensions in block 1:

- `.jpg`
- `.jpeg`
- `.jpe`
- `.jfif`

### Photo + video sibling pairs

Allowed image extensions for explicit image/video pairing in block 1:

- `.jpg`
- `.jpeg`
- `.jpe`
- `.jfif`
- `.heic`
- `.heif`

Allowed video extensions for explicit image/video pairing in block 1:

- `.mov`
- `.mp4`

### Required matching rule

Association is allowed only when all of the following are true:

- same source root
- same directory
- same basename stem
- known allowed extension combination
- no ambiguity

If multiple candidates of the same required role exist, block 1 must not auto-attach them.

## Exact main-file selection rules for block 1

### Rule order

1. if a RAW + JPEG pair exists, RAW is the main file and JPEG is associated
2. if an image + sidecar exists, image is the main file and sidecar is associated
3. if an image + video pair exists, image is the main file and video is associated
4. if multiple associated categories attach to one image, the image remains the main file and all valid associated files follow it
5. if none of the above apply, the scanned file is a single-file group

### Important simplification

Block 1 does not try to create one group out of multiple independent main-image candidates in the same directory.

It only groups files around a single clearly selected main file.

## New core module to add

Add a dedicated new core module:

- `src/media_manager/core/media_groups.py`

This should hold the first reusable grouping logic instead of burying it inside one CLI command.

## New dataclasses to add in block 1

### `MediaAssociationWarning`

Fields:

- `path: Path`
- `warning_code: str`
- `message: str`

### `MediaGroupMember`

Fields:

- `path: Path`
- `role: str`
- `extension: str`

Example roles:

- `main`
- `sidecar_xmp`
- `sidecar_aae`
- `raw_sibling`
- `jpeg_sibling`
- `paired_video`

### `MediaGroup`

Fields:

- `group_id: str`
- `source_root: Path`
- `main_path: Path`
- `group_kind: str`
- `members: tuple[MediaGroupMember, ...]`
- `association_warnings: tuple[MediaAssociationWarning, ...]`

Required convenience properties:

- `associated_paths`
- `total_file_count`
- `associated_file_count`

### `MediaGroupSummary`

Fields:

- `group_count: int`
- `single_file_count: int`
- `associated_file_count: int`
- `association_warning_count: int`
- `group_kind_summary: dict[str, int]`

## Required functions in block 1

### `build_media_groups(...)`

Input:

- scanned files or scan summary records needed to identify source root + relative path

Output:

- ordered list of `MediaGroup`

### `summarize_media_groups(...)`

Input:

- iterable of `MediaGroup`

Output:

- `MediaGroupSummary`

### `collect_leftover_files(...)`

Input:

- source root
- set of paths already consumed by the main operation
- options for hidden files and directory filtering if needed

Output:

- ordered list of leftover files still present under the source root

## Existing models to extend first

Block 1 should not try to refactor every command equally.

The first extensions should target the already active plan/execution flows.

### Extend organize path first

The current organize CLI already exposes structured payloads and journal entries.

First extension targets:

- organizer planning entries
- organize execution entries
- organize JSON payload
- organize execution journal entries

Required new organize-facing fields:

- `group_id`
- `group_kind`
- `main_file`
- `associated_files`
- `associated_file_count`
- `association_warnings`

### Extend rename path second

Same field shape where applicable:

- `group_id`
- `group_kind`
- `main_file`
- `associated_files`
- `associated_file_count`
- `association_warnings`

### Extend cleanup workflow report after that

The cleanup workflow already composes organize + rename reporting and execution.

Required cleanup summary extensions:

- `media_group_count`
- `group_kind_summary`
- `associated_file_count`
- `association_warning_count`
- `leftover_consolidation_requested`
- `leftover_file_count`
- `removed_empty_directory_count`
- `leftover_conflict_count`

## Leftover consolidation in block 1

### Exact behavior

Block 1 uses only one leftover mode:

- `off`
- `consolidate`

### Default

- default is `off`

### Exact target folder name

Default leftover folder name:

- `_remaining_files`

### Exact rules

After a successful apply-run for a source root:

1. compute files still present under the source root that were not consumed by the main operation
2. move those files into `<source_root>\_remaining_files`
3. preserve only a flat safe naming strategy in block 1, using suffixes when conflicts occur
4. remove empty subdirectories below the source root
5. never remove the source root itself

### Conservative simplification for block 1

Do **not** preserve the old nested directory tree inside `_remaining_files` in the first version.

Use a simple flat consolidation directory with conflict-safe renaming.

That is easier to reason about and easier to undo.

## Exact journal requirements for block 1

The current execution journal already stores reversible operations.

Block 1 extends journal entries, but does not require a schema version bump yet if the additional fields stay additive.

Each relevant entry should be able to include:

- `group_id`
- `group_kind`
- `main_file`
- `associated_files`
- `associated_file_count`
- `association_warnings`

For leftover-consolidation entries also include:

- `leftover_consolidation`: true
- `source_root`
- `undo_action`
- `undo_from_path`
- `undo_to_path`

### Important journaling rule

Do not hide associated-file operations inside only one parent entry.

The journal must retain enough per-file detail that undo can restore each moved file deterministically.

## Exact CLI options for block 1

### Organize

Add:

- `--include-associated-files`
- `--leftover-mode {off,consolidate}`
- `--leftover-dir-name <NAME>`

### Rename

Add:

- `--include-associated-files`

Rename should not receive leftover consolidation in the first implementation unless the behavior stays obviously safe.

### Cleanup
n
Add:

- `--include-associated-files`
- `--leftover-mode {off,consolidate}`
- `--leftover-dir-name <NAME>`

## Recommended defaults for block 1

- `--include-associated-files`: default `False` for the first shipping version of block 1
- `--leftover-mode`: default `off`
- `--leftover-dir-name`: default `_remaining_files`

Reason:

Block 1 should first be introduced as explicit opt-in behavior until the test surface proves it safe.

## Test focus for block 1

Block 1 should add focused tests for:

1. sidecar grouping (`.xmp`, `.aae`)
2. RAW + JPEG grouping
3. image + video grouping
4. ambiguous match handling produces warnings and no unsafe auto-attach
5. organize apply moves associated files together
6. rename apply renames associated files consistently
7. leftover consolidation moves remaining files and removes empty directories
8. execution journals contain reversible entries for associated files and leftovers
9. undo can reverse grouped operations and leftover moves

## Exact implementation order for block 1

1. add `core/media_groups.py`
2. add media-group tests
3. extend organize core/result path
4. extend rename core/result path
5. extend cleanup workflow report/execution path
6. extend execution-journal entry payloads
7. add CLI flags and JSON/text output
8. add undo coverage

## Success criteria for block 1

Block 1 is successful when:

- known associated files move/rename together with the main media file
- leftover consolidation is opt-in and safe
- grouped actions are visible in preview and JSON output
- execution journals contain enough information for reliable undo
- the implementation stays conservative and Windows-first
