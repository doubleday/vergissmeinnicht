---
name: openspec-select-change
description: Repo-local helper for selecting an OpenSpec change with low-friction fallbacks when no interactive question UI is available.
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: project-local
  version: "1.0"
---

Resolve which OpenSpec change to act on with the least friction possible in Codex.

## Rules

1. Run `openspec list --json` to inspect active changes.
2. If there are no active changes, report that and stop.
3. If there is exactly one active change, auto-select it and announce the selection.
4. If there are multiple active changes:
   - Use an interactive question tool if the environment supports one.
   - Otherwise, present a short numbered list in plain text and ask the user to reply with either the number or the exact change name.
5. When presenting numbered options:
   - Show at most 5 changes unless the user asked for all.
   - Prefer most recently modified changes first.
   - Mark the recommended default clearly when appropriate.
6. After the user replies with a number, resolve it to the corresponding change name and continue without asking them to retype the full identifier.

## Plain Text Fallback Format

Use this exact pattern when interactive selection is unavailable:

```md
Select a change:
1. change-one
2. change-two
3. change-three

Reply with the number or the exact change name.
```

## Notes

- This helper is meant to mimic the low-friction behavior of `AskUserQuestion` in environments that do not render interactive pickers.
- Prefer auto-selection over prompting whenever there is only one active change.
