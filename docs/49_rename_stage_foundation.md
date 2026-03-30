# Rename Stage Foundation

## Why this is the next functional block

The workflow now has:
- source selection
- target selection
- operation mode
- exact duplicate review
- cleanup summary foundation
- sorting foundation and first sorting builder work

The next meaningful block is the rename stage.

Right now the rename stage still behaves like a placeholder. That is no longer acceptable once sorting has a real builder path.

## Goal of this milestone

Introduce a reusable rename-planning core that can support:
- live rename previews
- reusable templates
- prefix and suffix block composition
- later QML builder integration

## First supported rename concepts

The initial rename core supports block-based naming.

Current block kinds:
- original stem
- year
- day
- month name
- ISO date
- readable date
- time (HH-MM-SS)

Current position support:
- prefix
- suffix

This already covers the most obvious user-facing early templates.

## Initial templates

The first template library includes:
- readable datetime + original name
- year + month name + day + time + original name
- date + original name

These templates are enough to replace the static rename placeholder with a real preview-driven rename stage.

## Why template and preview logic come first

The QML rename stage should not build filenames with ad-hoc string concatenation.
The preview behavior should be powered by a reusable planning layer.

That planning layer should later support:
- more block kinds
- custom separators
- order editing
- optional metadata-driven blocks
- validation and collision handling

## Next visible workflow step

After this core exists, the next UI task is:
- replace the rename placeholder page with a real rename builder
- show a template dropdown
- allow block manipulation for prefix/suffix composition
- show live filename previews for real source items

## Out of scope for this milestone

Do not mix these in yet:
- actual file rename execution
- metadata extraction beyond current timestamp-based preview inputs
- collision resolution strategy
- bulk exception editing

Those are later layers.
