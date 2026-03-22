## Context

The memory service now has a stable core contract and duplicate-write prevention, but it still cannot tell whether stored memories are actually being reused. Milestone C calls for quality controls that keep the store useful over time, and access tracking is the smallest next step that adds operational signal without changing the API boundary.

This change is intentionally narrower than supersession support. The current service already supports create, fetch, search, and archive with a simple archive-first lifecycle. Adding `last_accessed_at` fits that model because it records read activity on an existing record, while supersession would require new rules about record replacement, visibility, and history traversal.

## Goals / Non-Goals

**Goals:**

- Add a durable `last_accessed_at` field to the canonical memory record
- Define clear, observable rules for when read operations advance that field
- Keep the existing four-endpoint API boundary unchanged
- Preserve room for later supersession support without precommitting to replacement semantics now

**Non-Goals:**

- Defining a supersedes or superseded-by relation between memories
- Changing duplicate-write behavior or archive semantics beyond access timestamp updates
- Adding ranking, eviction, or cleanup policies that depend on access timestamps
- Tracking retrieval effectiveness or whether a client actually used a returned memory

## Decisions

Add `last_accessed_at` to the canonical record and initialize it at creation time.
Rationale: every created memory has at least one known access event at birth, which avoids nullable lifecycle ambiguity and keeps the record shape simple for clients.

Advance `last_accessed_at` on successful fetch-by-id and for memories returned in search results.
Rationale: these are the existing read paths where the system can observe that a memory was surfaced to a caller. Reusing current endpoints keeps the change within the established API surface.

Treat access tracking as a canonical-store concern.
Rationale: PostgreSQL already owns lifecycle and exact metadata. Persisting access timestamps there keeps the signal inspectable and independent of Qdrant internals.

Do not infer supersession from access patterns.
Rationale: a frequently accessed memory is not necessarily authoritative, and an infrequently accessed one is not necessarily obsolete. Supersession needs explicit lifecycle semantics in a later change.

## Risks / Trade-offs

[Updating timestamps on reads increases write traffic] -> Fetch and search will become read-plus-write operations in the canonical store. This is acceptable in the current local-first design because correctness and inspectability matter more than peak throughput.

[Search can touch multiple records per request] -> Advancing `last_accessed_at` for every returned memory may cause broad timestamp churn. This is still the simplest observable rule and avoids introducing ranking or threshold heuristics in this slice.

[Initializing `last_accessed_at` at creation may blur create versus read events] -> Clients will not be able to distinguish "never read after creation" from "read immediately after creation" using this field alone. That trade-off keeps the schema and contract smaller than introducing separate created-versus-accessed lifecycle markers.
