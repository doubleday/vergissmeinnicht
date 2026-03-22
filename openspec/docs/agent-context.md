# Agent Context

## What This Project Is

`vergissmeinnicht` is a self-hosted memory backend for coding agents, scripts, and local models. The first version should be boring on purpose: a small HTTP API backed by PostgreSQL and Qdrant, started locally through Docker Compose.

## What Matters Early

- Keep the public contract small and stable.
- Make stored memory inspectable outside the vector database.
- Optimize for determinism, debuggability, and restart-safe persistence.
- Delay auto-learning and framework-specific abstractions until explicit memory workflows work well.

## Initial API Boundary

- `POST /memories`
- `POST /memories/search`
- `GET /memories/{id}`
- `POST /memories/{id}/archive`

## Initial Data Model

- Canonical memory row in PostgreSQL
- Embedding and retrieval payload in Qdrant
- Required concepts: kind, scope, namespace, title, content, tags, source type, confidence, timestamps, archived flag, metadata

## Working Assumptions

- v1 writes are explicit, not inferred from conversation logs
- archive is preferred over delete
- exact filters should work before semantic retrieval is considered complete
- MCP and other adapters should sit on top of the same backend primitives rather than define their own storage behavior

## Near-Term Deliverables

1. Compose stack with FastAPI, PostgreSQL, and Qdrant
2. Memory API contract and typed request/response models
3. Persistence wiring for create, search, fetch, and archive
4. One thin adapter after the core API is stable
