## Why

The duplicate-write slice reduced write noise, but the service still has no durable signal for whether a memory is actually being revisited. The smallest useful next Milestone C increment is `last_accessed_at`, because it adds observable access tracking without forcing lifecycle decisions about how one memory replaces another.

This is the better next slice than supersession because the current contract already has stable fetch and search paths, while supersession would need broader rules for replacement semantics, archive interaction, and query visibility. Capturing access timestamps first keeps the change narrow, testable, and easy to validate before any richer lifecycle workflow is introduced.

## What Changes

- Extend the canonical memory record with a `last_accessed_at` timestamp for access tracking.
- Define when read operations update `last_accessed_at`, including fetch-by-id and returned search results.
- Clarify that create and archive operations do not set or advance `last_accessed_at` unless a later change explicitly expands that behavior.
- Keep supersession, replacement chains, and automatic consolidation out of scope for this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: extend the canonical record and read semantics to track when a memory was last accessed.

## Impact

- Introduces a delta spec under [`openspec/changes/track-memory-last-accessed-at/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/track-memory-last-accessed-at/specs/memory-service-core/spec.md)
- Affects the canonical memory schema plus fetch and search behavior in the API and persistence layer
- Defers supersession and broader lifecycle semantics so Milestone C can continue in smaller slices
