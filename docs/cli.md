# CLI Notes

## Current policy

The repository reset changes the role of the CLI.

The command-line interface is now the primary active product surface.

The old behavior of launching a desktop UI when no command was provided has been removed on purpose.

## Why the default changed

Starting the GUI by default made the repository feel more GUI-first than it actually should be during the reset.

The active direction is now:

1. scan / inspect foundations
2. organize and rename planning
3. state and idempotence
4. duplicates
5. workflows
6. GUI later

## Current commands

- `media-manager scan`
- `media-manager inspect`
- `media-manager organize`
- `media-manager rename`
- `media-manager duplicates`
- `media-manager gui` *(legacy, explicit only)*

## Legacy GUI note

The GUI still exists as a legacy surface.

It is intentionally no longer the default entry point.

If GUI dependencies are needed, install them explicitly:

```powershell
pip install -e .[gui,dev]
```

## Near-term direction

The next CLI expansion should add:

- richer inspect behavior
- later richer reporting

These commands should be built on the rebuilt core modules rather than bolted onto the older desktop-oriented structure.
