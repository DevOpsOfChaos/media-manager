# Home and Navigation Spec

## Home Page Goal

The home page must immediately communicate:
- this is a serious media cleanup application
- the workflow is the recommended path
- the user can start with a simple problem statement
- the UI is modern, large, centered, and calm

## Layout Rules

### Global layout
- Left side: narrow navigation rail
- Main content: centered and dominant
- No giant empty framed header bar above the content
- No old card-grid feeling
- Base window should feel intentionally compact; larger window sizes may reveal more space gracefully

### Left navigation rail
The rail should be visually restrained:
- narrower than the current experimental versions
- title smaller than the main page title
- nav buttons centered and evenly spaced
- active page state should use a subtle blue framed glow
- hover state across the whole app should visually match the active-style family instead of becoming dramatically brighter

### Language switch
Language switching remains a single button at top right.

Rules:
- one button only
- clicking toggles language
- flag changes when language changes
- default is English
- if user switches to German, the next app launch should restore German
- no wide extra toolbar only for the language button
- the control should sit cleanly in the top-right area of the content frame

## Home Content

### Main title
Centered, very large, modern font, bold.

### Subtitle
Short, centered, calmer than the title.

### Guided questionnaire
The questionnaire is the main home interaction:
- vertically stacked
- centered
- large buttons
- no side-by-side layout
- no extra descriptive paragraph inside each problem button unless genuinely needed
- button width should be based on content comfort, not almost full page width

Recommended visible options:
1. Full cleanup
2. Duplicates already handled, now organize
3. Already organized, mostly rename
4. Exact duplicate review only

### Dismiss
Below the questionnaire there should be a centered dismiss button.
It can be broader and slightly taller than before.

### Informational section
Below the questionnaire:
- “How it works”
- short explanation of the product idea
- visually clean and centered
- not buried below oversized problem buttons

## Navigation Strategy

Manual tool pages remain in navigation, but they must feel secondary.

The workflow should always be visually positioned as the preferred route unless the application already knows that the selected target was processed before and the user is intentionally resuming or reopening a previous optimization context.
