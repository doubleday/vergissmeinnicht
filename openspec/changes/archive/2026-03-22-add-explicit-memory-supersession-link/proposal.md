## Why

The next smallest useful Milestone C slice after `last_accessed_at` is explicit supersession metadata. The service needs a durable way to say "this newer memory replaces that earlier memory" without pulling in broader lifecycle cleanup such as merge rules, automatic archival, restore behavior, or replacement-aware search.

## What Changes

- Extend the canonical memory record with an optional `supersedes_memory_id` field that points from a newer memory to an earlier memory it explicitly supersedes.
- Allow create requests to supply `supersedes_memory_id` and persist that linkage when the referenced memory exists in the same namespace.
- Treat `supersedes_memory_id` as part of duplicate-write equivalence so explicit supersession intent is not erased by the existing dedupe rule.
- Clarify that supersession does not change archive state, search visibility, fetch behavior, or create any automatic reverse traversal in this slice.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: extend the canonical record and create semantics to support an explicit supersession link without adding broader lifecycle behavior.

## Impact

- Introduces a delta spec under [`openspec/changes/add-explicit-memory-supersession-link/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/add-explicit-memory-supersession-link/specs/memory-service-core/spec.md)
- Affects the canonical memory schema, create validation, and duplicate-write semantics in the API and PostgreSQL canonical store
- Preserves the existing four-endpoint API boundary and defers merge, restore, automatic archival, and search-time supersession handling
