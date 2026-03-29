# Architecture Overview

## Purpose

`vergissmeinnicht` is a self-hosted memory backend for coding agents, scripts, and local automation.

The architecture is intentionally conservative:

- a small HTTP API
- explicit writes
- inspectable storage
- simple local deployment

The goal is to make memory behavior understandable and debuggable before adding broader automation or smarter retrieval behavior.

## Core Shape

The current system is built around three main pieces:

- `memory-api` as the public HTTP surface
- PostgreSQL for canonical structured records
- Qdrant for vector retrieval

They run together locally through Docker Compose.

This split is deliberate:

- PostgreSQL is the source of truth for lifecycle, metadata, and auditability.
- Qdrant is used for semantic candidate retrieval.
- The API layer owns the public contract and combines exact filtering with retrieval behavior.

## Public API Boundary

The project keeps a narrow initial API boundary:

- `POST /memories`
- `POST /memories/search`
- `GET /memories/{id}`
- `POST /memories/{id}/archive`

This keeps the external contract stable while allowing internal storage and retrieval behavior to evolve.

## Data Model Stance

The memory model is designed to avoid a generic vector-store junk drawer.

Important concepts include:

- `kind`
- `scope`
- `namespace`
- `title`
- `content`
- `tags`
- `source`
- `confidence`
- timestamps
- `archived`
- `metadata`

The architectural idea is:

- canonical memory record in PostgreSQL
- embedding and retrieval payload in Qdrant

That gives the system both semantic retrieval and inspectable structured memory state.

## Retrieval Philosophy

The project treats retrieval as a staged problem rather than a single vector lookup.

High-level flow:

1. Apply exact filters such as namespace, scope, kind, or tags.
2. Use semantic retrieval to produce candidates.
3. Merge and return results through the API layer.

The guiding principle is:

- retrieval first
- automation later

In practice, that means:

- do not auto-store arbitrary chat content early
- prefer explicit store, search, and archive workflows
- measure retrieval quality separately from functional correctness

## Runtime Approach

The project is optimized first for local, repeatable operation.

That means:

- Docker Compose for the main stack
- persistent local data for PostgreSQL and Qdrant
- environment-based runtime configuration
- deterministic local embedding support for hermetic testing and fallback

Real embedding providers are supported as higher-signal evaluation paths, but they are not the baseline required for ordinary development.

## Adapter Strategy

The backend is intended to support multiple client surfaces without splitting behavior across app-specific stores.

The architectural stance is:

- one backend
- multiple adapters

Examples:

- Python client
- CLI
- MCP wrapper
- later agent-specific integrations

All of them should talk to the same core memory primitives rather than introducing separate storage contracts.

## Memory Hygiene

The system is expected to accumulate long-lived memory, so hygiene is part of the architecture, not an afterthought.

Key controls include:

- deduplication
- archive instead of delete
- confidence and source tracking
- `last_accessed_at`
- optional supersession support

The intent is to keep the memory store useful after repeated real-world use rather than letting it degrade into noisy vector history.

## Observability

Retrieval quality should be inspectable.

At a high level, the system should make it possible to reason about:

- query behavior
- retrieved ids
- latency
- relevance quality
- whether retrieval changes are helping or hurting

That is why retrieval evals are treated as a separate workflow rather than hidden inside ordinary unit or integration tests.

## Mem0 Positioning

Mem0 is treated as something to evaluate, not something to center the architecture around.

The project stance is:

- do not make Mem0 the public contract
- keep the project’s own API boundary stable
- treat Mem0, if used later, as a benchmark or replaceable backend component

This avoids premature lock-in while the core memory behavior is still being refined.

## Design Principles

The architecture follows a few consistent principles:

- Keep the public contract small.
- Prefer explicit memory workflows over automatic extraction.
- Keep storage inspectable outside the vector database.
- Separate functional correctness from retrieval-quality evaluation.
- Add adapters on top of stable backend primitives.
- Delay more aggressive ranking, automation, or framework-specific behavior until the core loop is trustworthy.

## Relationship To Other Docs

- [roadmap.md](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docs/roadmap.md) describes current milestones and priorities.
- [retrieval-evals.md](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docs/retrieval-evals.md) describes the retrieval evaluation workflow and its role.
- [semantic-search-comparison.md](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docs/semantic-search-comparison.md) explains how saved eval artifacts should be compared.

This document sits above those files and explains the architectural shape they fit into.
