## Why

The repository has project notes and a roadmap, but it does not yet have a narrow, reviewable OpenSpec change that defines the first stable contract. Before building infrastructure or application code, the project needs a clear specification for what a memory is and what the initial API must expose.

This is the right time to do it because the architecture direction is already clear, but the MVP can still sprawl if contract work and implementation work are bundled together. Capturing the contract separately keeps later changes smaller and easier to validate.

## What Changes

This change defines only the first external contract and canonical memory model.

- Define the canonical fields and taxonomy for a memory record.
- Define the four initial API operations: create, search, get by id, and archive.
- Specify observable behavior for validation, fetch, and archive semantics.
- Leave Docker, FastAPI wiring, database schema, Qdrant collections, and search implementation details to follow-up changes.

## Capabilities

### New Capabilities

- `memory-service-core`: Core HTTP memory service contract for explicit create, search, fetch, and archive operations.

### Modified Capabilities

- None.

## Impact

- Introduces the first product capability spec under [`openspec/changes/define-core-memory-contract/specs/memory-service-core/spec.md`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/changes/define-core-memory-contract/specs/memory-service-core/spec.md)
- Establishes the baseline API boundary that later implementation changes must satisfy
