## Why

`POST /memories/search` currently relies on PostgreSQL text matching and deterministic ordering, which keeps the contract stable but does not yet deliver the semantic retrieval flow already implied by the architecture. This is the right next broader slice because Milestone B explicitly calls for search that merges exact filters with semantic retrieval, and the codebase already writes embeddings and retrieval payloads into Qdrant.

## What Changes

- Add the first semantic search flow for query-present `POST /memories/search` by retrieving candidate memory identifiers from Qdrant and resolving them through PostgreSQL.
- Preserve the existing search request shape and current endpoint so callers continue using the canonical memory API without learning retrieval internals.
- Keep PostgreSQL as the canonical filter and record store by reapplying namespace, scope, kind, tag, archived, and superseded rules before returning results.
- Preserve the current browse-style PostgreSQL path when no query is present.
- Define explicit non-goals for this slice: no reranking experiments, source weighting, new endpoints or flags, conversation extraction, background reindex jobs, adapter work, multi-stage fusion tuning, or major lifecycle changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `memory-service-core`: change search requirements so query-present searches can use semantic candidate retrieval from Qdrant while preserving existing PostgreSQL-backed filtering and canonical response behavior.

## Impact

- Introduces a delta spec under [`openspec/changes/add-semantic-memory-search/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/add-semantic-memory-search/specs/memory-service-core/spec.md).
- Affects the search flow in [`memory_service.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/memory_api/src/memory_api/services/memory_service.py), PostgreSQL-backed search filtering in [`postgres.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/memory_api/src/memory_api/services/postgres.py), and Qdrant retrieval integration in [`qdrant_store.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/memory_api/src/memory_api/services/qdrant_store.py).
- Adds targeted tests for semantic candidate retrieval, filter preservation, canonical record return behavior, and query-less search stability.
- Preserves the current four-endpoint API boundary and avoids contract expansion into reranking, lifecycle automation, or adapter-specific behavior.
