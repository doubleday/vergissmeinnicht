## Context

The memory service already stores a `source` object in the canonical PostgreSQL record and returns it through all four public endpoints, but the current contract only requires `source.type`. That makes provenance inconsistent across writers because different clients can send differently cased or padded values, and there is no small stable field for identifying the originating tool or workflow beyond a generic type.

This Milestone C slice should improve auditability without turning source tracking into a broader provenance system. The existing code path is already explicit and synchronous: create validates a `MemoryCreate` payload, PostgreSQL stores the canonical row, and fetch/search/archive return that stored record. That makes source normalization a good fit for the canonical model rather than a new endpoint or background process.

## Goals / Non-Goals

**Goals:**

- Define a minimal stable canonical `source` shape that is more useful for auditing than `type` alone
- Normalize `source` deterministically at write time so all returned records expose the same representation
- Keep the current four endpoints and lifecycle semantics unchanged
- Limit the slice to inspectable provenance fields already carried by the canonical record

**Non-Goals:**

- Adding source history, arrays, merge rules, restore/delete flows, or traversal across related memories
- Inferring source data automatically from conversations, adapters, or retrieval pipelines
- Weighting search results by source or introducing source-based trust semantics
- Adding new API operations, background jobs, or richer provenance documents with URLs, timestamps, or actor identities

## Decisions

Normalize `source.type` as a trimmed lowercase canonical token.
Rationale: `type` is already the required provenance field, and lowercasing after trimming removes accidental variation without introducing a new taxonomy.
Alternative considered: trim-only normalization. Rejected because `Manual`, `manual`, and ` MANUAL ` would still remain distinct stored values even though they carry the same practical meaning in this codebase.

Add an optional `source.name` field as a trimmed short label and omit it when blank.
Rationale: a minimal caller/origin label makes records more debuggable across multiple explicit writers while staying neutral about actor identity or trust semantics.
Alternative considered: require a richer source object with IDs, URLs, or timestamps. Rejected because it would overfit specific clients and expand the provenance contract beyond this narrow slice.

Apply source normalization in the canonical write path and return the stored normalized shape unchanged on create, fetch, search, and archive.
Rationale: PostgreSQL is already the inspectable source of truth for canonical memory data. Normalizing once before persistence keeps all endpoints consistent and avoids endpoint-specific reformatting rules.
Alternative considered: normalize only on response serialization. Rejected because the stored row would remain inconsistent and less auditable when inspected directly.

Keep duplicate-write equivalence unchanged.
Rationale: this slice is about provenance clarity, not memory identity. Reusing the current dedupe rule avoids accidental lifecycle or lineage changes.
Alternative considered: include normalized `source` in duplicate detection. Rejected because it would broaden the meaning of duplicate active writes and could create extra active records for the same memory content.

## Risks / Trade-offs

[Canonical lowercase `source.type` may discard client-preferred presentation] -> Mitigation: treat `type` as a machine-stable provenance token and keep human-facing specificity in the optional `source.name`.

[Dropping blank `source.name` can hide whether a client intentionally sent an empty label] -> Mitigation: prefer a cleaner canonical record over preserving non-meaningful empty values; clients that care can send an explicit non-empty label.

[A minimal `type` plus `name` envelope may still be too small for future provenance needs] -> Mitigation: keep the contract narrow now and reserve richer provenance modeling for a separate change once real usage shows which fields matter.

## Migration Plan

1. Update the request/response model so the canonical `source` object supports required `type` plus optional `name`.
2. Normalize `source` in the create path before PostgreSQL persistence so new rows are stored canonically.
3. Ensure fetch, search, archive, and duplicate-create responses all serialize the stored normalized shape consistently.
4. Add targeted tests for type normalization, optional name trimming/omission, and stable source shape across returned records.
5. No data backfill is required for this slice because it is being applied before broader external adoption.

## Open Questions

None for this slice. Richer provenance semantics, source validation taxonomies, and source-aware retrieval behavior remain deferred.

