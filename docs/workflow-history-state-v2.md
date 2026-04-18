# Workflow History / State v2

This block adds a small but useful history layer to the workflow shell.

## New commands

- `media-manager workflow history --path <DIR>`
- `media-manager workflow last --path <DIR>`
- `media-manager workflow last --path <DIR> --command organize`

## What it scans

The history commands look recursively for JSON files and recognize two record types:

- command run logs
- execution journals

Unknown JSON files are ignored.

## Why this matters

The project now has several commands that can write structured logs and journals.

Without a small history view, those files remain useful but inconvenient.

This workflow-shell history layer gives the user a lightweight way to:

- see what ran recently
- see whether apply mode was requested
- see which command produced a log or journal
- inspect the newest matching record for a command

## Scope of v2

This is still a file-based history view.

It is not yet a persistent database, a timeline UI, or a full execution browser.

Those can build on top of this later.
