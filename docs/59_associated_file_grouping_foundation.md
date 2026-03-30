# Associated-file grouping foundation

This step adds a foundation for file relationships such as RAW+JPEG and media sidecars.

## Added module
- `src/media_manager/associated_files.py`

## Purpose
The project now has a small relationship model for files that belong together.
This is important because duplicate cleanup, move, copy, or rename logic should not later orphan sidecars or split related media sets by accident.

## Current model
The module currently distinguishes:
- primary media files
- known sidecars
- other files

### Known primary media examples
- JPG / JPEG / PNG / HEIC / HEIF
- CR2 / CR3 / NEF / ARW / ORF / RAF / RW2 / DNG
- MP4 / MOV / MKV / AVI / MTS / M2TS

### Known sidecar examples
- XMP
- AAE
- SRT
- THM
- LRV
- WAV

## Current entry points
- `associated_key_for_path(path)`
- `classify_associated_path(path)`
- `group_associated_files(paths)`
- `build_associated_file_map(paths)`

## Current safety behavior
A relationship group is only emitted when:
- there is at least one primary media file
- and more than one related file exists for the shared stem

So pure sidecar-only groups are ignored for now.

## Why this matters
Before this step, the duplicate path could become increasingly powerful without any dedicated concept of related files.
That would be dangerous later for real execution, because deleting or moving one file from a set might silently orphan XMP, AAE, SRT, THM, LRV, or WAV companions.

This foundation does not wire protection into execution yet, but it gives the project the first clean backend building block for that work.
