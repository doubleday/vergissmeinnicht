## Why

The current memory service accepts every valid create request as a new record. That is fine for bootstrapping, but it will quickly degrade memory quality once agents and scripts repeat the same write across multiple runs.

This is the right next change because the core API contract already exists, and duplicate prevention is the smallest quality-control slice that directly supports the roadmap without pulling in broader lifecycle work yet.

## What Changes

- Define duplicate-write behavior for `POST /memories` within the existing core memory capability.
- Specify how the service distinguishes a new memory from a duplicate candidate using canonical fields rather than retrieval internals.
- Require the API to return a stable, observable result when a create request matches an existing active memory.
- Clarify that broader memory hygiene features such as `last_accessed_at`, rich supersession, and automatic consolidation remain out of scope for this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: extend create semantics to prevent duplicate or near-duplicate writes from producing uncontrolled record growth.

## Impact

- Introduces a delta spec under [`openspec/changes/prevent-duplicate-memory-writes/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/prevent-duplicate-memory-writes/specs/memory-service-core/spec.md)
- Affects create-memory behavior in the API and canonical persistence flow
- Defers schema expansions for access tracking and supersession so implementation can remain small and reviewable
