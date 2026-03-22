## Context

The current service creates a new canonical memory row for every valid `POST /memories` request and then mirrors that row into Qdrant. That behavior is easy to reason about, but it does nothing to protect the store from repeated writes by the same agent loop, script, or operator workflow.

This change is intentionally narrower than the full "memory quality controls" milestone. It focuses only on preventing duplicate growth at write time while preserving the existing four-endpoint API boundary and the current archive-first lifecycle model.

## Goals / Non-Goals

**Goals:**

- Prevent repeated equivalent writes from creating multiple active records
- Keep duplicate detection explainable and inspectable in the canonical store
- Preserve the existing external endpoint surface while making create behavior more robust
- Leave room for later additions such as `last_accessed_at` and supersession without locking those designs now

**Non-Goals:**

- Defining a general-purpose fuzzy matching or semantic reranking system
- Adding update, delete, merge, or bulk-cleanup endpoints
- Introducing a full supersession graph or replacement workflow
- Tracking read access or retrieval feedback signals in this change

## Decisions

Use canonical-field duplicate checks at write time.
Rationale: duplicate prevention should be deterministic, debuggable, and independent of embedding behavior. The simplest useful rule is to compare normalized canonical inputs such as namespace, scope, kind, title, and content before inserting a new row.

Treat duplicate detection as part of create semantics, not as a separate endpoint.
Rationale: callers already know how to create memories. Folding duplicate checks into the existing create flow improves quality without expanding the v1 API boundary.

Return the existing active memory when a duplicate is detected.
Rationale: this preserves idempotent behavior for repeated writes and gives clients a stable canonical record. Rejecting duplicates as errors would force every client to add special-case handling with little product value.

Ignore archived memories for duplicate blocking in this first slice.
Rationale: archived records exist for auditability, and broad reactivation or supersession rules would expand scope. A request that matches only archived records may create a new active memory until a later change defines richer lifecycle semantics.

Keep near-duplicate handling conservative.
Rationale: broad fuzzy matching risks false positives and unexpected write suppression. This change should only block duplicates that meet a clearly specified equivalence rule, leaving more aggressive hygiene to later work.

## Risks / Trade-offs

[Equivalent-match rules may be too strict] -> Some near-duplicates will still be stored. This is acceptable because false negatives are safer than false positives in the first quality-control slice.

[Returning an existing record changes create semantics] -> Clients that assumed every create returns a fresh identifier will need to tolerate idempotent responses. This is manageable because the endpoint contract still returns a canonical memory record.

[Archived records are excluded from duplicate blocking] -> A previously archived memory can be recreated as active. This is an intentional trade-off to avoid entangling this change with restoration or supersession behavior.
