## Why

The service already accepts `confidence` and uses it later as a secondary ordering signal, but today it persists whatever in-range float the client sends. That leaves canonical records harder to inspect because semantically equivalent values can be stored with arbitrary precision or floating-point noise, which makes confidence-based behavior less auditable during debugging.

The next narrow Milestone C slice should make stored confidence values more inspectable without expanding the API boundary or redefining retrieval semantics. This is a canonicalization policy for an existing field, not a broader confidence model.

## What Changes

- Normalize `confidence` to a deterministic canonical value at create time before persistence.
- Define that create, fetch, search, and archive responses return the stored normalized `confidence` value for that memory.
- Keep the existing inclusive `0.0` to `1.0` validation boundary and current four endpoints unchanged.
- Explicitly defer ranking redesign, source weighting, merge/restore/delete flows, supersession traversal, background jobs, and any new endpoint surface.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `memory-service-core`: refine the canonical memory record and create behavior so stored `confidence` values are deterministic and easier to audit across the existing four endpoints.

## Impact

- Introduces a delta spec under [`openspec/changes/normalize-memory-confidence/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/normalize-memory-confidence/specs/memory-service-core/spec.md)
- Affects the memory API request normalization path and PostgreSQL canonical record persistence for `confidence`
- Adds targeted tests around deterministic confidence normalization and consistent returned values across create, fetch, search, archive, and duplicate-create paths
- Preserves the existing four-endpoint API boundary and avoids ranking redesign, lifecycle expansion, provenance weighting, or new retrieval workflows
