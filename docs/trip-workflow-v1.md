# Trip workflow v1

Trip workflow v1 builds a date-range-based collection from one or more source folders.

## Goal

Select media files whose resolved capture date falls inside a user-provided inclusive date range,
then place them into a trip collection using either hard links or copies.

## Command

```powershell
media-manager trip --source C:\Photos --target D:\MediaCollections --label Italy_2025 --start 2025-08-01 --end 2025-08-14
```

## Collection layout

The workflow creates collection paths below:

```text
<target>/Trips/<year>/<label>/<source_name>/<relative_source_path>
```

Example:

```text
D:/MediaCollections/Trips/2025/Italy_2025/Phone/DCIM/IMG_1234.JPG
```

## Modes

- `link` (default): creates hard links for matched files
- `copy`: copies matched files into the collection

## Safety and idempotence

- files outside the date range are marked as skipped
- existing matching targets with identical file size are skipped
- existing targets with different size are marked as conflicts
- apply mode only executes entries with `planned` status

## Notes

Hard links are used instead of symbolic links because they are usually more practical on Windows without
additional privilege setup. Hard links require the source and target to be on the same filesystem.
