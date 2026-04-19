# Release Smoke Checklist

This checklist is meant for larger handoff blocks, ZIP deliveries, and branch states that are supposed to be stable enough for commit and push.

It focuses on the current repository reality:

- core first
- CLI first
- Windows first
- English first
- workflow/profile/bundle/history layer already important

## 1. Scope the change honestly

Before running tests, classify the block:

### A. Safe docs-only block

Typical examples:

- new docs files
- repository map improvements
- playbooks and checklists

Expected minimum:

```powershell
pytest -q
```

### B. Narrow feature block

Typical examples:

- one new helper in `core.state.history`
- one new workflow CLI flag
- one additive profile filter

Expected minimum:

- direct new test file
- nearby compatibility tests
- full `pytest -q`

### C. Wide compatibility block

Typical examples:

- `__init__.py` export changes
- JSON output shape changes
- dataclass constructor changes
- bundle serialization changes

Expected minimum:

- all nearby tests
- all likely indirect compatibility tests
- full `pytest -q`
- explicit review of import and JSON contracts

## 2. Check import surfaces first

When any of these change, import breakage becomes likely:

- `src/media_manager/__init__.py`
- `src/media_manager/core/state/__init__.py`
- `src/media_manager/core/workflows/__init__.py`

Questions to ask:

- did a previously exported helper disappear?
- did an import path move without a re-export?
- did a cumulative local state differ from public `main`?

## 3. Check JSON contracts

For any CLI JSON output change, ask:

- are old top-level fields still present?
- did an old field move under a nested object?
- was a field renamed instead of extended additively?
- does the no-match case still behave as expected?

Do not reshape JSON casually.

## 4. Check Windows path behavior

Always think about:

- slash vs. backslash matching
- portable bundle-relative paths
- `Path` vs. `str` expectations in tests and payloads

Typical failure mode:

- logic seems fine on POSIX-style assumptions
- Windows collection or string checks fail immediately

## 5. Check dataclass and constructor compatibility

If a dataclass is instantiated positionally anywhere in tests or old code, adding fields can silently break older calls.

Before shipping:

- verify field order
- use defaults for additive fields where possible
- avoid reordering old positional fields unless the whole call surface is updated

## 6. Run the right tests in the right order

Recommended order for nontrivial blocks:

1. direct new test file
2. nearby compatibility tests
3. full `pytest -q`

Never treat step 1 as enough.

## 7. Write the handoff clearly

Every ZIP handoff should include:

- what is in the ZIP
- what the block changes
- what was actually tested
- exact commands to run
- exact `git add`, `git commit`, `git push`

Avoid claiming a block is broadly green when only a narrow test slice was checked.

## 8. Stop conditions

Do **not** hand off yet if any of these are true:

- only the new test file was run
- `pytest -q` was not considered for a compatibility-sensitive change
- an `__init__` surface changed and was not checked broadly
- JSON output shape changed without compatibility review
- a Windows path case was not considered

## 9. Good default for bigger blocks

For larger blocks that touch code, this is the safe baseline:

```powershell
pytest -q <new-test-file>
pytest -q <nearby-compat-tests>
pytest -q
```

That should be treated as normal, not exceptional.
