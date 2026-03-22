## Context

The memory service already has a stable core contract, duplicate-write prevention, archiving, and `last_accessed_at`. Milestone C still lacks an explicit way to record that one memory supersedes another, which makes later cleanup and audit workflows harder because replacement intent only exists implicitly in content and timestamps.

This change must stay narrower than general lifecycle cleanup. The current API boundary remains `create`, `search`, `get by id`, and `archive`, and PostgreSQL remains the canonical owner of lifecycle metadata. The smallest coherent addition is a one-way canonical link from the newer memory to the superseded memory, with validation rules that fit the existing create path.

## Goals / Non-Goals

**Goals:**

- Add an explicit optional `supersedes_memory_id` field to the canonical memory record
- Allow create requests to persist that field when the referenced memory already exists in the same namespace
- Preserve supersession intent in duplicate-write handling instead of collapsing distinct linkage states together
- Keep fetch, search, and archive responses observably stable aside from exposing the new canonical field

**Non-Goals:**

- Automatically archiving, hiding, or re-ranking superseded memories
- Adding reverse links such as `superseded_by_memory_id` or chain traversal endpoints
- Supporting merge, restore, or reconciliation workflows
- Requiring kind, scope, title, or content compatibility between the new memory and the superseded memory
- Inferring supersession from timestamps, content similarity, or access patterns

## Decisions

Use a single forward link named `supersedes_memory_id`.
Rationale: the create path already produces the newer record, so storing a pointer from the new record to the older one is the smallest explicit representation. A reverse link would duplicate state or require extra write coordination.

Expose `supersedes_memory_id` as an optional canonical field and optional create input.
Rationale: clients need to both declare and observe the linkage through the existing API shape. Making the field nullable keeps records that do not participate in supersession simple and backward-compatible.

Validate only that the referenced memory exists and shares the same namespace.
Rationale: namespace is the existing tenant boundary for dedupe and retrieval. Requiring existence prevents dangling pointers, while avoiding tighter constraints keeps the slice implementation-agnostic and narrow.

Allow superseding either active or archived memories.
Rationale: supersession is an explicit lineage statement, not an archive action. Blocking archived targets would couple this slice to restore and lifecycle cleanup semantics that are intentionally deferred.

Include `supersedes_memory_id` in duplicate-write equivalence.
Rationale: without this, a create request carrying new supersession intent could be collapsed into an existing active duplicate that lacks the linkage, making the new field unreliable. Matching on the field preserves explicit intent while keeping the dedupe model simple.

Do not change search, fetch, archive, or ranking semantics based on supersession.
Rationale: exposing the link is useful immediately, while any visibility or lifecycle policy would require additional product decisions about canonical winners, historical browsing, and cleanup behavior.

## Risks / Trade-offs

[Explicit links without visibility rules can surface both old and new memories in search] -> This is acceptable for the slice because it records authoritative intent first. Later lifecycle work can decide whether superseded memories should be hidden, archived, or deprioritized.

[Including `supersedes_memory_id` in duplicate matching allows multiple otherwise-identical active records when they point at different predecessors] -> This is intentional. Different supersession targets represent different lineage claims and should not be collapsed by the current dedupe rule.

[Allowing archived targets may create chains that cross lifecycle states] -> That complexity already exists conceptually once audit history is preserved. Deferring policy keeps this change small while still preserving the linkage needed for later cleanup work.

## Migration Plan

Add the new canonical column as nullable so existing records remain valid without backfill.

Extend create validation and persistence to store the supplied link when present.

Leave all existing records with `supersedes_memory_id = NULL` until a future explicit write creates linkage.

## Open Questions

None for this slice. Search suppression, automatic archival, reverse traversal, and merge semantics are intentionally deferred to later lifecycle changes.
