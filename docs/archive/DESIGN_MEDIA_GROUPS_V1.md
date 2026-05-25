# Design: Media Groups and Source Leftover Consolidation (V1)

This file defines the first conservative version of:

- associated files / media groups
- source leftover consolidation
- the result and journaling requirements needed for later GUI support

The design assumes the current active baseline:

- CLI-first / core-first
- cleanup workflow already uses explicit options, report models, and execution reports
- execution journals already exist and already support reversible entries

## Goals

1. Treat a main media file together with known related files as one operational unit.
2. Reduce broken leftovers in source folders after organize / rename / cleanup apply-runs.
3. Keep the behavior conservative, explainable, previewable, and undoable.
4. Add the logic in a way that later fits a service/application layer.

## Non-goals for V1

V1 does **not** try to solve every media relationship.

V1 will not include:

- heuristic or AI-based grouping
- cross-directory fuzzy matching
- grouping based only on capture timestamps
- vendor-specific database formats
- aggressive metadata package relocation without clear basename rules

## Core concept

The operational unit is no longer only a single file.

For eligible files, the operational unit becomes a **media group**:

- one main media file
- zero or more associated files
- one shared preview/apply decision
- one shared execution/journal interpretation

## Conservative matching rules for V1

A file may pull associated files only when the mapping is explicit.

### Required conditions

An associated file is attached only when all of the following are true:

1. same source root
2. same directory as the main file
3. same basename stem
4. associated extension is explicitly allowed
5. association is unambiguous

If the match is ambiguous, V1 must not auto-attach the file.

Instead it should:

- leave the file ungrouped
- record a warning / association warning
- allow later manual review

## Supported associated-file categories in V1

### Category A — sidecars

Allowed examples:

- `.xmp`
- `.aae`

Meaning:

- these follow the main file operation
- if the main file is copied/moved/renamed, the sidecar follows consistently

### Category B — RAW + JPEG sibling pairs

Allowed examples:

- `IMG_1001.CR3` + `IMG_1001.JPG`
- `DSC_0001.NEF` + `DSC_0001.JPG`
- `P1234567.ORF` + `P1234567.JPG`

Rule:

- one file is marked as the main file for the current operation
- the sibling file is recorded as an associated file
- both move together

V1 must keep this conservative:

- only same directory
- only same stem
- only known media-pair extensions

### Category C — photo + video sibling pairs

Allowed examples:

- `IMG_2001.HEIC` + `IMG_2001.MOV`
- `IMG_2001.JPG` + `IMG_2001.MOV`

Rule:

- only explicit same-stem sibling pairs
- only known image/video combinations
- no fuzzy matching

### Category D — optional exact-basename side files (disabled by default)

This category should not be enabled in the first implementation unless needed.

Examples could later include:

- `.json`
- `.srt`
- `.txt`

For V1 these should stay out unless we have a concrete justified use case.

## Main-file selection rules

When a group contains multiple media files, V1 must still identify one main file for planning/reporting.

Conservative selection priority for V1:

1. RAW file over JPEG sibling
2. image file over sidecar
3. explicit photo/video pair keeps the image as main file and video as associated file, unless the command itself is video-led
4. if no special rule applies, keep the originally scanned file as main file

## Required new core data model concepts

### MediaGroup

V1 should introduce an explicit core model similar to:

- `group_id`
- `main_path`
- `associated_paths`
- `group_kind`
- `association_warnings`
- `total_file_count`

`group_kind` examples:

- `single`
- `sidecar`
- `raw_jpeg_pair`
- `photo_video_pair`
- `mixed`

### Group-aware planning/execution

Planning and execution code should operate on groups, not only single paths, where supported.

This does **not** require rewriting every command at once.

V1 should target first:

1. organize execution
2. rename execution
3. cleanup workflow reporting/execution

## Source leftover consolidation (V1)

### Intent

After a successful apply-run, remaining files inside a source may optionally be consolidated.

### Default

- disabled by default
- only available for apply-runs
- never active for preview-only runs

### Behavior

For each source root separately:

1. identify files still remaining under the source root after the main operation
2. move those remaining files into one dedicated leftover folder under that same source root
3. remove empty directories below the source root

Suggested default leftover directory name:

- `_remaining_files`

The folder should be per source root, not global.

Examples:

- `C:\Phone\_remaining_files`
- `D:\OldBackup\_remaining_files`

### Important safety rules

- never delete leftover files in V1
- only move them
- only remove directories that are empty after consolidation
- never remove the source root itself
- if a leftover-file conflict occurs inside `_remaining_files`, use a safe conflict strategy such as suffixing or skipping with a warning

### Review distinction

V1 should already reserve the concept of a separate manual-review path.

But the first implementation may still use only `_remaining_files` if needed.

Longer term we want to distinguish:

- normal leftovers
- manual-review/problem files

## Required result/report fields

The current cleanup flow already returns structured payloads and execution sections.

V1 should extend that style with explicit group and leftover reporting.

### Required summary fields

- `media_group_count`
- `group_kind_summary`
- `associated_file_count`
- `association_warning_count`
- `leftover_consolidation_requested`
- `leftover_file_count`
- `leftover_directory_count`
- `removed_empty_directory_count`
- `leftover_conflict_count`

### Required per-entry / per-execution fields

For executed or planned entries, we should be able to tell:

- which path was the main file
- which associated files followed it
- which group kind applied
- whether leftover consolidation moved additional files afterward

## Required journaling / undo behavior

The current execution journal schema already stores per-entry reversible actions.

V1 should preserve that approach and extend it.

### Journal entries for media-group operations

If a main file move/copy/rename also moved associated files, journaling must capture them explicitly.

The journal must let undo restore:

- the main file action
- each associated-file action
- leftover consolidation moves
- empty-directory removals only when we can model them safely

### Minimum journal extension for V1

Each journal entry should be able to include group context:

- `group_id`
- `group_kind`
- `main_file`
- `associated_files`
- `association_warnings`

For leftover consolidation entries we should also record:

- `leftover_consolidation`: true
- original source path
- leftover target path
- undo action (`move_back` or equivalent)

## CLI surface guidance for V1

CLI must come after core modeling, but we should already define intended flags.

### Proposed conservative flags

For organize / rename / cleanup where applicable:

- `--include-associated-files`
- `--leftover-mode {off,consolidate}`
- `--leftover-dir-name <NAME>` (optional, default `_remaining_files`)

Defaults:

- associated files: off or narrowly on by command policy (decision to finalize during implementation)
- leftover mode: `off`

My implementation recommendation for V1:

- make `--include-associated-files` default to **on** for safe known sidecars/pairs once the behavior is well tested
- keep `--leftover-mode` default **off**

## Recommended implementation order

1. define core models for media groups
2. implement explicit matching rules and tests
3. make organize/rename execution group-aware
4. extend cleanup report/execution payloads
5. extend journaling / undo for grouped actions and leftovers
6. add CLI flags and text/JSON output
7. only later expose the same behavior through a GUI/service layer

## Immediate implementation scope recommendation

The first implementation block should focus on:

- sidecars: `.xmp`, `.aae`
- RAW+JPEG sibling pairs
- photo+video sibling pairs for explicit same-stem cases
- per-source `_remaining_files` consolidation
- journal and undo support for all moved associated files and leftovers

That is enough to create real product value without making the first version too risky.
