## Context

The repository currently contains product notes and the stable `memory-service-core` contract, but it does not yet contain a runnable application stack. This change needs to introduce the first working local environment without expanding scope into adapters, ranking strategy, or memory hygiene features that belong to later milestones.

The design has to cover multiple runtime concerns at once: container orchestration, API process boot, canonical persistence in PostgreSQL, retrieval index connectivity to Qdrant, and basic readiness checks. The main constraint is to keep these choices inspectable and reversible so later iterations can improve search behavior without replacing the local bootstrap story.

## Goals / Non-Goals

**Goals:**

- Start the full local stack with one command
- Persist PostgreSQL and Qdrant state across container restarts
- Provide a minimal API runtime that can connect to both stores and expose health or readiness signals
- Make backing data easy to inspect directly during development
- Preserve compatibility with the existing `memory-service-core` contract as the implementation target

**Non-Goals:**

- Defining adapter protocols such as MCP, CLI, or SDK support
- Implementing advanced semantic ranking, reranking, or deduplication
- Solving production deployment, high availability, or backup concerns
- Introducing automatic conversation extraction or asynchronous learning pipelines

## Decisions

Use Docker Compose as the single local orchestration entry point.
Rationale: the roadmap prioritizes one-command startup, and Compose keeps service topology explicit for local development. An alternative would be running services separately through ad hoc scripts, but that makes startup less reproducible and weakens the inspection story.

Run three primary services in the first slice: `memory-api`, `postgres`, and `qdrant`.
Rationale: these are the minimum components needed to satisfy the planned local foundation. An `embed-worker` remains optional and is excluded for now because it introduces asynchronous behavior before the basic synchronous stack is proven.

Treat PostgreSQL as the canonical record store and Qdrant as the retrieval index from the start.
Rationale: this matches the architecture direction already captured in project notes and avoids a temporary single-store implementation that would later need migration. The alternative of storing everything only in PostgreSQL is simpler short term, but it would delay validating the dual-store integration that the roadmap already assumes.

Add explicit startup and health checks for each service plus an API-level readiness check for downstream dependencies.
Rationale: local bootstrap work fails most often at the integration boundary, not at process startup. A readiness check that verifies API access to PostgreSQL and Qdrant gives a testable signal that the stack is usable. The alternative of exposing only a generic liveness endpoint would not tell developers whether the stack is actually ready to serve memory operations.

Define environment-driven configuration for connection strings, collection names, and embedding settings even if some values are not fully exercised in the first implementation.
Rationale: this keeps the stack configurable without baking local assumptions into code or Compose. The alternative of hardcoded local defaults is faster initially, but it makes later provider or environment changes more error-prone.

## Risks / Trade-offs

[The first change spans infrastructure and application bootstrapping] → Mitigation: keep the behavioral surface narrow, limit the change to local operability, and treat advanced retrieval logic as out of scope.

[Qdrant may be present before semantic search quality is implemented] → Mitigation: treat Qdrant connectivity and inspectability as success criteria in this slice, not full ranking sophistication.

[Environment configuration can become overdesigned too early] → Mitigation: include only settings needed to boot the local stack and reserve provider-specific expansion for later changes.

[Container health signals may be flaky if they depend on too much application logic] → Mitigation: separate basic process health from dependency readiness and keep readiness probes shallow and deterministic.
