## Context

The current search path is fully PostgreSQL-backed. When a query is present, PostgreSQL applies `ILIKE` matching across `title` and `content`, orders the matching rows deterministically, and returns canonical records. Qdrant is already part of the write path, but only as a sink for embeddings and retrieval payloads; query-time search does not yet use it.

This change is the first broader vertical slice for the intended dual-store design. It needs to introduce semantic retrieval without expanding the public API, without shifting lifecycle authority away from PostgreSQL, and without pulling in ranking experiments or background maintenance work. The main constraint is preserving the current endpoint contract while making query-present search observably semantic.

## Goals / Non-Goals

**Goals:**

- Route query-present `POST /memories/search` through a semantic candidate retrieval step in Qdrant.
- Reapply the existing PostgreSQL filters for namespace, scope, kind, tags, archived visibility, and superseded suppression before returning results.
- Return canonical `MemoryRecord` responses from PostgreSQL so timestamps, lifecycle fields, and normalized shapes remain authoritative.
- Preserve the current query-less browse path and its deterministic ordering semantics.

**Non-Goals:**

- Adding new endpoints, search flags, adapter-specific behavior, or client-visible retrieval internals.
- Running reranking experiments, weighted score fusion, source weighting, or broader ranking-policy tuning.
- Adding background reindex jobs, recovery jobs, or lifecycle changes to write, archive, or supersession behavior.
- Implementing conversation extraction, reverse-link traversal, or replacing PostgreSQL as the canonical record store.

## Decisions

Use Qdrant only for query-present semantic candidate retrieval.
Rationale: this is the smallest change that makes semantic search real. Query-less searches remain a browse path, which avoids surprising callers and keeps the current PostgreSQL-only behavior intact for non-query requests.
Alternative considered: route all searches through Qdrant. Rejected because browse-style requests do not need semantic retrieval and would force unnecessary coupling between pagination, lifecycle filters, and the vector index.

Keep PostgreSQL as the canonical filter and record resolver after candidate retrieval.
Rationale: PostgreSQL already owns archived state, supersession rules, `last_accessed_at`, and the canonical memory shape. Resolving Qdrant candidates through PostgreSQL preserves those rules without duplicating lifecycle logic into payload filters or trusting Qdrant payloads as the response source.
Alternative considered: filter directly in Qdrant using payload constraints and return payload-derived records. Rejected because it would duplicate lifecycle logic, weaken auditability, and risk drift from canonical records.

Resolve query embeddings in the service layer, then pass candidate IDs into PostgreSQL search.
Rationale: the service already owns embedder access and coordinates write-time embedding. Extending that orchestration to search keeps Qdrant focused on vector retrieval and PostgreSQL focused on canonical row filtering.
Alternative considered: make PostgreSQL search embed queries or call Qdrant directly. Rejected because it would blur storage boundaries and make the persistence layer responsible for embedding concerns.

Preserve deterministic result ordering by honoring Qdrant candidate order first, with PostgreSQL tie-breakers for stability.
Rationale: once semantic retrieval is introduced, Qdrant rank becomes the primary relevance signal for query-present searches. PostgreSQL should preserve that candidate ordering while still applying deterministic `updated_at` and `id` tie-breakers when needed.
Alternative considered: re-sort filtered candidates purely in PostgreSQL using the existing textual ordering rules. Rejected because it would largely erase the value of semantic retrieval and bias results back toward substring matches.

Retrieve more candidate IDs from Qdrant than the final API `limit`, then apply PostgreSQL filters and truncate to the request limit.
Rationale: PostgreSQL filters can remove some semantically relevant candidates, so the search path needs a bounded oversampling step to avoid empty or underfilled responses when valid matches exist. This remains a simple implementation concern, not a fusion or tuning exercise.
Alternative considered: ask Qdrant for exactly `limit` candidates. Rejected because post-filtering would make the result count too fragile once namespace, tag, or archived constraints are applied.

## Risks / Trade-offs

[Semantic ranking may surface results that do not contain obvious substring hits] -> Mitigation: define that behavior explicitly at the contract level for query-present searches and keep canonical filters unchanged so the broader result set is still constrained predictably.

[PostgreSQL filtering after Qdrant retrieval can drop many candidates and reduce recall] -> Mitigation: oversample candidate IDs in a bounded way before PostgreSQL filtering and keep the first slice intentionally simple rather than introducing complex multi-stage retrieval.

[Qdrant rank and PostgreSQL lifecycle state can diverge from payload metadata over time] -> Mitigation: treat Qdrant as an index of candidate IDs only and always resolve the final response from PostgreSQL.

[This change introduces a stronger runtime dependency on Qdrant availability for query-present search] -> Mitigation: keep the dependency explicit in the design and tests, while preserving the query-less PostgreSQL browse path as-is.

## Migration Plan

No API migration is required because the request and response schema stay unchanged.

Implementation should add Qdrant query-time retrieval support, update the search orchestration to merge candidate IDs with PostgreSQL filters, and extend tests to cover semantic retrieval with existing filter behavior.

Rollback is straightforward: revert the query-present search path to the previous PostgreSQL-only implementation while keeping the existing write-time Qdrant indexing intact.

## Open Questions

None for this slice. Fallback behavior, advanced fusion, reranking, and reindex operations remain intentionally deferred.
