## Context

The project is intended to become a shared memory backend for multiple coding agents and local automation workflows. The immediate need is a stable contract that future code, infrastructure, and adapters can build against without locking the implementation too early.

The surrounding architecture direction is already understood, but this change is intentionally narrower than the overall MVP. It focuses on what clients can send and receive, and on the lifecycle semantics of stored memories.

## Goals / Non-Goals

**Goals:**

- Define the minimal public contract for the first version
- Keep the API small enough to survive internal rewrites
- Define a canonical memory shape and allowed taxonomy values
- Make later implementation changes validate against an agreed behavioral baseline

**Non-Goals:**

- Choosing exact storage engines or schemas
- Defining Docker Compose, service topology, or deployment concerns
- Specifying embedding models, reranking, or retrieval internals
- Automatic memory extraction from chats or background learning behavior

## Decisions

Use explicit write operations only in v1.
Rationale: explicit writes make the system easier to debug and evaluate across Claude, Codex, scripts, and local models.

Keep four API endpoints in the first public contract.
Rationale: `create`, `search`, `get`, and `archive` are sufficient to prove the backend and preserve room to evolve internals later.

Define a constrained taxonomy up front.
Rationale: limiting `kind` and `scope` early prevents the first version from becoming an unstructured memory dump.

Specify behavior, not implementation.
Rationale: later changes should be free to choose FastAPI modules, SQL shape, Qdrant payload design, and execution flow as long as the observable contract remains stable.

## Risks / Trade-offs

Restricting the v1 API to explicit operations may feel slow compared with auto-memory approaches.
Trade-off: this is acceptable because determinism and observability matter more than convenience at the start.

Keeping the contract small may force later follow-up changes for features that seem adjacent.
Trade-off: that is preferable to one oversized MVP change that mixes decisions across product, infrastructure, and implementation.
