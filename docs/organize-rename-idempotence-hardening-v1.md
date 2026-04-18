# Organize / Rename Idempotence Hardening v1

This block tightens two important CLI behaviors without dragging the project back into UI work.

## Organize

The organizer now treats an already-existing target more carefully:

- if the target exists with different bytes, the row stays a conflict
- if the target exists with identical bytes, the row is treated as already satisfied and skipped
- apply-time execution re-checks the target instead of blindly assuming the plan is still valid

That makes repeated organize runs safer and more idempotent than a simple file-size comparison.

## Rename

The renamer executor now catches per-file rename failures and records them as structured error rows instead of letting one failing rename crash the whole run.

## Why this matters

These are small-looking changes, but they improve real product behavior:

- repeated runs become less noisy
- existing organized targets are handled more honestly
- apply steps are more resilient to filesystem changes between planning and execution
- rename failures remain inspectable through CLI/run-log flows
