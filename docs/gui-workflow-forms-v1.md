# GUI workflow forms v1

This block introduces a small form-model layer for the new shell instead of jumping
straight to a large GUI rewrite.

What is included:

- workflow form field metadata for the major workflows
- `media-manager shell --dump-forms`
- `media-manager shell --preview-form <workflow>`
- the shell window now shows a lightweight field summary for selected workflows

Why this matters:

- a future modern GUI can build real forms from these models
- the shell can now expose which inputs a workflow actually needs
- headless inspection stays possible for testing and scripting
