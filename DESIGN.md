# Local AI Song Studio Design System

## Product Context

Local-only personal music production workstation for a single operator.
The interface is not public-facing. It should feel like a focused studio desk
where the user can move from lyric drafting to prompt planning to music
generation without leaving the page.

## Aesthetic Direction

- Tone: dark studio workspace, warm and technical at once
- Feeling: organized, deliberate, slightly industrial
- Visual metaphor: a music craft bench with stacked tools and active panels
- Priority: keep the workflow visible end-to-end on one screen

## Core Design Principle

One page should support the full loop:

1. Select project
2. Pick lyric version
3. Choose prompt preset
4. Generate music spec
5. Generate audio
6. Review results and logs

Do not split the core workflow across multiple screens unless the screen is
strictly for a deep editor.

## Typography

- Primary UI text: `Inter`, `ui-sans-serif`, system fallback
- Numeric / technical metadata: `ui-monospace`, `SFMono-Regular`, `Menlo`
- Headings: same family, but with stronger weight and tighter tracking
- Avoid decorative fonts; the product should feel practical, not playful

## Color

The app is dark-mode only.

### Palette

- Background: near-black charcoal
- Surface 1: deep slate panel
- Surface 2: slightly lighter control surface
- Border: muted blue-gray line
- Text: soft off-white
- Muted text: cool gray
- Accent 1: mint-green, for active generation and primary actions
- Accent 2: soft blue, for supportive emphasis
- Danger: restrained red, used sparingly

### Color intent

- Primary actions should stand out immediately
- Secondary controls should recede but remain legible
- Status and selection states should be visible without neon intensity

## Layout

### Overall structure

- Full-page workspace with a strong top header
- Three-column thinking, but flexible in width:
  - Left rail: project, presets, versions, history
  - Center workbench: lyrics, spec generation, music generation
  - Right rail: jobs, results, audio, logs, playback
- On smaller screens, collapse to a single column in the same order

### Information hierarchy

1. Current project and current state
2. Main generation controls
3. Latest outputs
4. Supporting logs and metadata

### Card behavior

- Cards should feel like workbench modules
- Use clear borders and layered depth
- Keep spacing compact enough to support dense data
- Avoid oversized marketing-style whitespace

## Motion

- Minimal motion only
- Use subtle hover elevation and state transitions
- Generation states should animate through status text, not flashy effects
- No decorative parallax, no excessive motion

## Component Style

### Buttons

- Primary: mint-to-blue gradient for generate actions
- Secondary: flat dark surface with border
- Ghost: low-emphasis outline style
- Button labels should describe work, not decoration

### Inputs

- Dark filled inputs with clear border
- Compact height
- Labels in uppercase small text
- Show values and metadata clearly

### Panels

- Use stacked panels to make the page feel like a studio desk
- Result panels should support long text, metadata, and logs
- Keep audio and job state visible at the same time

## One-Page Workflow

The page should present the workflow in this order:

1. Project selection and active preset
2. Lyrics version and short-form structure
3. Music spec generation
4. Audio generation
5. Result list, playback, and metadata
6. Logs and publish info

This order should be visible at a glance even before the user interacts.

## Screen Sections

### Left rail

- Project picker
- Prompt preset picker
- Song structure
- Lyrics version
- Quick project metadata

### Center workbench

- Main generation controls
- Editable music spec summary
- Generate spec button
- Generate music button
- Current prompt / plan preview

### Right rail

- Job status
- Recent outputs
- Selected audio details
- Playback controls
- Logs

### Bottom strip

- LRC
- Publish info
- Re-render / regenerate actions
- File-level metadata

## Visual Personality

- Serious, but not cold
- Functional, but not sterile
- Compact, but not cramped
- Studio-like, but not cluttered

## Decisions Log

- Dark mode only
- One-page workflow
- No public-facing marketing language
- No light theme
- Studio/workbench metaphor instead of app-dashboard generic styling

