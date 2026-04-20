# API proposal: Media Groups Block 1A

This file defines the concrete Python-facing API for the first implementation step.

Block 1A does **not** yet change CLI behavior.

Block 1A only adds:

- core media-group models
- grouping logic
- grouping summary logic
- testable pure functions

It is designed to attach cleanly to the current organizer and renamer models, which already use structured plan and execution dataclasses.

## New module

Add:

- `src/media_manager/core/media_groups.py`

## New dataclasses

### `MediaAssociationWarning`

```python
@dataclass(slots=True, frozen=True)
class MediaAssociationWarning:
    path: Path
    warning_code: str
    message: str
```

Allowed initial warning codes:

- `ambiguous_sidecar`
- `ambiguous_raw_jpeg_pair`
- `ambiguous_photo_video_pair`
- `unsupported_association`

### `MediaGroupMember`

```python
@dataclass(slots=True, frozen=True)
class MediaGroupMember:
    path: Path
    role: str
    extension: str
```

Initial allowed roles:

- `main`
- `sidecar_xmp`
- `sidecar_aae`
- `jpeg_sibling`
- `raw_sibling`
- `paired_video`

### `MediaGroup`

```python
@dataclass(slots=True, frozen=True)
class MediaGroup:
    group_id: str
    source_root: Path
    main_path: Path
    group_kind: str
    members: tuple[MediaGroupMember, ...]
    association_warnings: tuple[MediaAssociationWarning, ...] = ()
```

Required convenience properties:

```python
@property
    def associated_paths(self) -> tuple[Path, ...]: ...

@property
    def total_file_count(self) -> int: ...

@property
    def associated_file_count(self) -> int: ...
```

Initial allowed `group_kind` values:

- `single`
- `sidecar`
- `raw_jpeg_pair`
- `photo_video_pair`
- `mixed`

### `MediaGroupSummary`

```python
@dataclass(slots=True, frozen=True)
class MediaGroupSummary:
    group_count: int
    single_file_count: int
    associated_file_count: int
    association_warning_count: int
    group_kind_summary: dict[str, int]
```

## Input model for block 1A

Block 1A should work from the existing scan model, not from CLI strings.

Use the already existing scanned-file model from the scanner layer.

Primary input type for grouping:

```python
Iterable[ScannedFile]
```

That keeps the grouping code reusable for organize, rename, cleanup, inspect, and later GUI/application services.

## Required pure functions

### `build_media_groups`

```python
def build_media_groups(files: Iterable[ScannedFile]) -> list[MediaGroup]:
    ...
```

Behavior:

- groups files by `(source_root, parent_directory, stem)`
- creates at most one main-file-led media group per eligible scanned file
- preserves deterministic ordering
- returns one `MediaGroup` per main media file / single file unit

Ordering requirement:

- order by `source_root`
- then by relative parent path
- then by main filename

### `summarize_media_groups`

```python
def summarize_media_groups(groups: Iterable[MediaGroup]) -> MediaGroupSummary:
    ...
```

### `find_group_for_path`

```python
def find_group_for_path(groups: Iterable[MediaGroup], path: Path) -> MediaGroup | None:
    ...
```

Purpose:

- helper for later organizer/renamer integration
- makes it easy to attach grouping info to existing plan entries

### `build_media_group_index`

```python
def build_media_group_index(groups: Iterable[MediaGroup]) -> dict[Path, MediaGroup]:
    ...
```

Purpose:

- direct path-to-group lookup for later planner/executor code

## Helper functions allowed internally

These do not need to be exported publicly, but are expected in the module:

- `_normalize_extension(path: Path) -> str`
- `_is_raw_extension(ext: str) -> bool`
- `_is_jpeg_extension(ext: str) -> bool`
- `_is_sidecar_extension(ext: str) -> bool`
- `_is_photo_video_image_extension(ext: str) -> bool`
- `_is_photo_video_video_extension(ext: str) -> bool`
- `_build_group_id(source_root: Path, main_path: Path) -> str`
- `_select_main_candidate(files_in_bucket: list[ScannedFile]) -> ScannedFile`

## Bucket model for grouping

For block 1A, grouping should happen in deterministic buckets:

```python
(source_root, parent_directory, stem)
```

Within one bucket, classify file extensions into categories.

### Category priority in one bucket

1. RAW media
2. image media
3. video media
4. sidecars

This supports the current block-1 main-file rule set.

## Exact block-1A behavior by bucket

### Case 1: no valid association candidates

Return one `single` group with one `main` member.

### Case 2: image + sidecar

Return one group:

- main = image
- associated = sidecar(s)
- kind = `sidecar`

### Case 3: RAW + JPEG

Return one group:

- main = RAW
- associated = JPEG
- kind = `raw_jpeg_pair`

### Case 4: image + video

Return one group:

- main = image
- associated = video
- kind = `photo_video_pair`

### Case 5: image + sidecar + paired video or RAW + JPEG + sidecar

Return one group with kind `mixed`.

### Case 6: ambiguous matches

Do not attach the ambiguous candidate.

Return the safest valid group and add warnings.

If a bucket becomes fully unclear, fall back to conservative singles.

## Exact integration target for block 1B and later

The current organizer and renamer models already expose these entry types:

- `OrganizePlanEntry`
- `OrganizeExecutionEntry`
- `RenamePlanEntry`
- `RenameExecutionEntry`

Later blocks should extend those entries with grouping fields.

But block 1A should not modify those models yet.

That keeps block 1A isolated and easy to test.

## Test file to add in block 1A

Add a dedicated pure-core test file, for example:

- `tests/test_core_media_groups_v1.py`

Minimum test cases:

1. single JPG returns `single`
2. JPG + XMP returns one `sidecar` group
3. HEIC + AAE returns one `sidecar` group
4. CR3 + JPG returns one `raw_jpeg_pair` group with CR3 as main
5. JPG + MOV returns one `photo_video_pair` group with JPG as main
6. JPG + XMP + MOV returns one `mixed` group
7. ambiguous duplicates of the same role produce warnings
8. summary counts match expected totals
9. index lookup resolves each member path to the same group

## Success criteria for block 1A

Block 1A is done when:

- media-group detection exists as a reusable core module
- the logic is deterministic and conservative
- no CLI behavior has changed yet
- tests prove sidecar/pair detection and ambiguity handling
- the output is ready to be attached to organize/rename in the next block
