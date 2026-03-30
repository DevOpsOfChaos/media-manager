# State, Resume, and Manual Tools Spec

## Purpose

This document captures the intended behavior for:
- workflow persistence
- hidden state in the target system
- crash recovery
- re-opening already optimized targets
- the relationship between guided workflow and manual tools

## Hidden workflow state

The product should persist workflow-relevant state inside the target system in a hidden way.

The goal is not cosmetic convenience.
The goal is to make long-running workflows survivable and reusable.

## Why this matters

The guided workflow can become long and decision-heavy.
Without persistent hidden state, the user loses trust because a crash, accidental close, or restart can destroy too much progress.

The state model should therefore allow the system to:
- recover after crashes
- recover after accidental closure
- re-open an existing optimized target and continue from previous work
- validate whether the current folder state still matches the last known workflow data

## Minimum stored information

The hidden workflow state should eventually include at least:
- target identity
- selected source folders at the time of processing
- selected operation mode
- current workflow stage
- duplicate decisions
- associated-file decisions or notes
- dry-run plan or plan history
- sorting configuration
- rename configuration
- trip/session definitions where relevant
- last known scan metadata
- completion / partial completion status

## Resume behavior

When the user opens a target that was already processed before, the system should:
1. detect the hidden state
2. compare it against current visible reality
3. decide whether the old state still looks trustworthy enough to reuse
4. continue from the appropriate point if it does
5. degrade gracefully if it does not

The software should not blindly trust stale stored data.
It should revalidate quickly and then build on it.

## Manual tools strategy

Manual tools should remain available, but they should not undermine the workflow direction.

### Principles
- workflow remains the preferred product path
- manual tools should reuse as much workflow logic as possible
- users who start manual tools in fresh, unknown targets should be encouraged to use the workflow first
- users who start manual tools in already-known targets should benefit from existing hidden state

### Fresh target behavior
If a user starts a manual tool outside a previously processed target:
- source selection may still be required
- the UI may gently point out that workflow-first offers better structure and better context
- the message should be informative, not patronizing

### Known target behavior
If a user starts a manual tool on a target that the software already knows:
- hidden state should be reused
- repeated warnings should be reduced
- the user should be able to continue working without redoing every earlier step

## Trip/session tool relationship

The trip/session tool should also benefit from stored target state.
It should not feel disconnected from the rest of the product.

If trip/session definitions were previously created, the user should be able to:
- reopen them
- adjust them
- continue from existing definitions instead of rebuilding everything from zero

## Execution history value

Later, execution history can help with:
- explaining what changed in a previous run
- showing what was copied, moved, or deleted
- making future re-cleanup of the same target safer

## Implementation guidance

This persistence layer should be treated as a product feature, not just a technical detail.
It directly affects user trust and willingness to run long workflows.

The implementation should therefore prioritize:
- explicit state ownership
- validation before reuse
- stable schema evolution
- clear separation between hidden persisted state and visible user-facing data
