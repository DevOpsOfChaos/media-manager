# QML duplicate detail state integration

## Current constraint

The connector used during this work session could create new files on a feature branch, but it could not overwrite the existing `src/media_manager/qml_app.py` file directly.

## What was added on this branch

- `src/media_manager/qml_app_fixed.py`
- `notes/qml_app_fixed_for_duplicate_detail.py`

The canonical runnable candidate is `src/media_manager/qml_app_fixed.py`.

## What this fixes

This branch restores the duplicate detail state path expected by `src/media_manager/qml/Main.qml`:

- duplicate detail translations
- duplicate detail properties
- duplicate detail selection state
- `openDuplicateGroup(...)`
- `closeDuplicateGroup()`
- `selectDuplicateCandidate(...)`
- `chooseDuplicateKeepNewest()`
- `chooseDuplicateKeepOldest()`
- `keepSelectedDuplicateCandidate()`
- row `index` values needed by the QML table action button

## Local test command

From an editable install in the repository root:

```bash
python -m media_manager.qml_app_fixed
```

## Recommended merge follow-up

After confirming that the fixed module works locally, copy the content of `src/media_manager/qml_app_fixed.py` into `src/media_manager/qml_app.py` and remove the temporary helper files.
