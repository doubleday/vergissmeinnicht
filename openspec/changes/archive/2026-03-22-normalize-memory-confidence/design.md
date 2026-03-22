## Context

The memory service stores `confidence` on the canonical PostgreSQL record, validates only that it falls within `0.0` to `1.0`, and returns it unchanged through the existing endpoints. Search ordering can already use that stored number as a tie-breaker, but the current write path does not define a canonical precision or normalization rule.

For this codebase, the smallest useful Milestone C improvement is to make stored confidence values easier to inspect and compare directly. This should stay narrower than a retrieval-policy change: PostgreSQL remains the canonical store, the four current endpoints remain unchanged, and no new trust semantics should be inferred from metadata, source, or lifecycle state.

## Goals / Non-Goals

**Goals:**

- Define one deterministic canonical representation for stored `confidence`
- Apply the normalization in the create path so the persisted value is auditable
- Keep create, fetch, search, and archive responses consistent for the stored value
- Preserve the current four endpoints and existing range validation boundary

**Non-Goals:**

- Redesigning search ranking or changing the ordering tuple beyond using the stored canonical value
- Adding source-weighting, trust inference, or metadata-derived confidence behavior
- Changing duplicate-write semantics, archive behavior, supersession workflows, or retrieval backends
- Adding background jobs, data backfills, or any new endpoint or request field

## Decisions

Normalize `confidence` to three decimal places using deterministic decimal rounding before persistence.
Rationale: three decimals are small enough to make records readable and comparable while preserving materially different scores in this codebase. It removes noisy precision without turning confidence into a coarse bucketed label.
Alternative considered: leave precision unconstrained and only document the range. Rejected because it does not improve auditability or explainability of stored values.

Use exact decimal normalization semantics rather than relying on raw binary float behavior.
Rationale: the point of this slice is deterministic canonicalization. Defining the normalization in decimal terms avoids implementation-dependent artifacts such as storing `0.30000000000000004`-style values.
Alternative considered: use Python's default float rounding behavior. Rejected because it is less explicit and harder to reason about when debugging stored values.

Normalize on the canonical create path and return the stored value unchanged from create, fetch, search, and archive.
Rationale: PostgreSQL is already the inspectable source of truth for canonical memory data. Normalizing before persistence keeps endpoint responses aligned with what is actually stored.
Alternative considered: normalize only when serializing responses. Rejected because the database row would remain harder to audit directly.

Preserve the existing `0.0` to `1.0` inclusive validation rule and do not add a new precision error.
Rationale: write-time normalization is a smaller change than rejecting clients for harmless extra precision. This keeps the API forgiving while still making the stored record deterministic.
Alternative considered: reject values with more than three decimal places. Rejected because it would create avoidable validation failures without improving the stored representation.

## Risks / Trade-offs

[Very close confidence values may collapse to the same normalized value] -> Mitigation: treat `confidence` as a coarse inspectable signal, not a high-precision ranking metric, and keep this slice explicitly limited to canonicalization.

[Pre-existing rows may retain older precision until rewritten] -> Mitigation: limit the change to new writes in this slice and defer any backfill or migration policy unless mixed-precision records become a real operational problem.

[Clients may expect their original formatting to round-trip exactly] -> Mitigation: document that `confidence` is part of the canonical stored record and may be normalized on write, just like other canonical fields in this service.

## Migration Plan

1. Add deterministic confidence normalization to the create-path model or validation layer.
2. Ensure PostgreSQL stores the normalized confidence value and returned canonical records preserve that stored value.
3. Add targeted tests for normalization precision and cross-endpoint consistency.
4. No backfill is required for this slice.

## Open Questions

None for this slice. Ranking redesign, provenance-aware weighting, and broader confidence semantics remain intentionally deferred.
