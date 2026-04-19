# Testing and Compatibility Checklist

This checklist is for changes that touch CLI, state helpers, workflow helpers, profiles, bundles, or history.

It exists to reduce regressions caused by small local changes that silently break unrelated parts of the repository.

## 1. Before changing code

Check these first:

- Which package `__init__.py` files export the touched helpers?
- Which CLI modules import those helpers through package re-exports?
- Which JSON shapes are already covered by tests?
- Which Windows path forms are part of the current behavior?
- Which older tests cover compatibility indirectly?

## 2. Export and import safety

When adding or changing helpers, verify:

- `src/media_manager/__init__.py`
- `src/media_manager/core/state/__init__.py`
- `src/media_manager/core/workflows/__init__.py`

Common failure mode:

- new helper added in one module
- direct local tests pass
- broader collection fails because package-level re-export was forgotten

## 3. JSON contract safety

Never assume a JSON payload can be reshaped just because a new test wants more fields.

Prefer:

- keep existing top-level fields
- add new fields additively
- avoid removing or nesting old fields unless the whole repo is migrated intentionally

Common examples of risky changes:

- converting top-level values into nested `entry` payloads
- changing `path` semantics
- switching strings to `Path` objects in serialized or test-facing values

## 4. Windows path safety

On this project, Windows is the main platform.

When paths participate in:

- JSON payloads
- portable bundle records
- contains-filters
- relative path comparisons

verify both:

- slash form: `family/cleanup.json`
- backslash form: `family\cleanup.json`

For portable stored bundle paths, prefer normalized slash form.
For local path matching, normalize both sides before comparing.

## 5. Test construction safety

Avoid hand-written fake payloads when real save/load helpers already exist.

Better:

- build a valid payload with the real helper
- write it
- load it again
- assert on the real roundtrip result

This reduces false positives and false negatives caused by incomplete fixtures.

## 6. Small test runs are not enough

A new block is not really ready if only the obviously related new test passes.

Minimum mindset:

- direct new test
- adjacent compatibility tests
- a broader targeted subset
- full `pytest -q` before calling a block green

## 7. Required targeted checks by change type

### State/history changes

Run at least:

```powershell
pytest -q tests/test_core_history*.py
pytest -q tests/test_cli_workflow_history*.py
pytest -q
```

### Workflow/profile/bundle changes

Run at least:

```powershell
pytest -q tests/test_core_workflow*.py
pytest -q tests/test_cli_workflow*.py
pytest -q tests/test_workflow_profile_selection_filters.py
pytest -q
```

### Core state export changes

Run at least:

```powershell
pytest -q tests/test_core_run_log.py
pytest -q tests/test_core_execution_journal.py
pytest -q tests/test_core_history_artifacts.py
pytest -q tests/test_core_undo.py
pytest -q
```

## 8. Watch for these repeated failure patterns

- forgotten package re-export
- overwrite of a cumulative file with an older partial version
- returning dicts where tests expect ordered object lists
- changing `Path` versus `str` semantics
- silent JSON shape drift
- fixing one direct test while breaking collection elsewhere

## 9. Good delivery standard

A block is in good shape when:

- syntax is clean
- exports are intact
- direct tests pass
- adjacent compatibility tests pass
- broad repo test run passes
- the update can be applied as simple exchange files without follow-up manual surgery

## 10. Practical release habit

For this repository, the safest routine is:

1. make the change
2. run the direct targeted tests
3. run at least one broader adjacent slice
4. run `pytest -q`
5. only then package the exchange files
