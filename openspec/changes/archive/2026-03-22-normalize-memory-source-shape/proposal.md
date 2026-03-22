## Why

The current contract only requires `source.type`, which leaves stored provenance too loose to audit consistently when different clients write to the same backend. The next narrow Milestone C slice should make source tracking more inspectable and debuggable without expanding the API boundary or taking on broader provenance workflows.

## What Changes

- Tighten the canonical `source` contract from "includes at least `type`" to a small stable shape that preserves a required normalized `type` and an optional normalized `name`.
- Require deterministic normalization of `source` values on create so stored records use one canonical representation for write, fetch, search, and archive responses.
- Clarify that the service preserves this normalized `source` envelope as part of the canonical memory record without changing duplicate-write rules, retrieval behavior, or lifecycle semantics.
- Explicitly defer broader provenance features such as source merges, source chains, automatic source extraction, trust weighting, restore/delete flows, and new endpoint surface.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: refine the canonical memory record and create behavior so `source` is returned in a deterministic minimal shape that improves auditability across the existing four endpoints.

## Impact

- Introduces a delta spec under [`openspec/changes/normalize-memory-source-shape/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/normalize-memory-source-shape/specs/memory-service-core/spec.md)
- Affects the memory API request/response schema, source validation and normalization logic, and PostgreSQL canonical record persistence
- Adds targeted tests around canonical source normalization on create and consistent source shape in returned memory records
- Preserves the existing four-endpoint API boundary and avoids merge, restore, delete, chain traversal, automatic extraction semantics, background jobs, or retrieval redesign
