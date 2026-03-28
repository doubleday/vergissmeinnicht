## Context

The repository already exposes a small stable HTTP contract and already uses `httpx` directly in smoke tests, integration tests, and evaluation tooling. Milestone D now needs the smallest reusable adapter layer that can sit between that API and later consumers such as a CLI or an MCP wrapper.

The constraint is to stay boring. This slice should not invent higher-level memory workflows, protocol bridges, or plugin abstractions. It only needs to remove repeated raw-HTTP wiring while keeping the public contract fixed at create, search, fetch, and archive.

## Goals / Non-Goals

**Goals:**

- Add a thin typed Python client for the four existing memory API endpoints.
- Keep the client importable from the existing installed package rather than introducing another distribution boundary.
- Reuse the existing canonical request and response shapes so client and service stay aligned.
- Provide a minimal transport seam for base URL, timeout, and injected `httpx` behavior to support tests and later adapters.
- Keep implementation and verification small enough to be the first Milestone D slice.

**Non-Goals:**

- Add MCP in the same slice.
- Add a CLI in the same slice.
- Expand the public API surface beyond the four memory endpoints.
- Introduce async and sync client variants in the first slice.
- Add retries, auth plugins, caching, batching, or adapter-specific abstractions.

## Decisions

### Add one sync `MemoryApiClient` first

The first slice should provide a synchronous client with one method per public operation: create, search, get by id, and archive.

Rationale:

- It is the smallest usable abstraction over the existing service.
- The repository already uses synchronous `httpx` in scripts and tests, so this fits current usage without widening scope.
- Later async support can be added as a separate slice if an MCP server or another consumer proves it necessary.

Alternatives considered:

- Add sync and async clients together. Rejected because it doubles API surface and test burden before there is a concrete async consumer.
- Skip the client and build MCP or CLI directly on raw `httpx`. Rejected because it duplicates transport, serialization, and error handling in the next adapter slice.

### Keep the client in the existing `memory_api` package

The client should live inside the package that is already built and installed by the project instead of creating a separate SDK package now.

Rationale:

- The current wheel configuration already packages `memory_api/src/memory_api`, so this is the narrowest packaging move.
- It avoids introducing another versioning and distribution concern before there are external consumers beyond this repository.
- It keeps the first adapter slice focused on behavior rather than packaging ceremony.

Alternatives considered:

- Create a separate Python package immediately. Rejected because it adds build and release complexity before the client boundary has been validated.
- Keep the client internal-only in scripts. Rejected because Milestone D needs a reusable adapter boundary, not another private helper.

### Reuse the canonical Pydantic models at the client boundary

The client should accept and return typed request and response models aligned to the existing canonical contract rather than inventing adapter-specific DTOs in this slice.

Rationale:

- The contract is already stable and small.
- Reusing the existing shapes keeps serialization boring and reduces duplicate schema definitions.
- It keeps future adapter work centered on the same four request and response types.

Alternatives considered:

- Duplicate a separate set of client-only models. Rejected because it creates schema drift risk without a clear benefit at this size.
- Expose untyped `dict` payloads. Rejected because the stated goal is a typed client.

### Keep the adapter boundary at HTTP transport and error mapping only

The client should own base URL joining, JSON serialization, response parsing, and predictable translation of non-success HTTP responses into client exceptions. Adapters built on top of the client should own user-facing commands, protocol mapping, retries, and orchestration.

Rationale:

- This keeps the client reusable by both a future CLI and a future MCP wrapper.
- It prevents this slice from smuggling CLI or MCP policy into the shared layer.
- A narrow exception boundary makes higher-level adapters easier to implement consistently.

Alternatives considered:

- Add command-oriented helper methods such as "remember rule" or "find project memories". Rejected because they are adapter policy, not API contract.
- Add retry and backoff behavior to the client. Rejected because retry policy belongs to the calling adapter or application context.

## Risks / Trade-offs

- [A sync-only client may not fit a future async consumer directly] -> Mitigation: keep the method surface small so a later async companion can mirror it without redesigning the contract.
- [Reusing existing models couples the client package to current server schema modules] -> Mitigation: keep the public API boundary fixed to the canonical models and treat later schema extraction as a separate packaging slice if needed.
- [Keeping the client in the existing package may delay a future standalone SDK split] -> Mitigation: preserve a clean module boundary so extraction remains mechanical if outside consumers appear.
- [Thin error mapping can still leave adapters deciding how to present failures] -> Mitigation: define a small predictable exception surface and leave presentation concerns to the adapter layer.

## Migration Plan

1. Add the new client module inside the existing installed package.
2. Expose one typed synchronous client class and its narrow exception surface.
3. Add unit tests using injected HTTP transport and one client-level integration path against the live API.
4. Document the client as the first Milestone D adapter boundary.
5. Defer CLI and MCP work to later changes that consume the client rather than bypassing it.

Rollback:

- Remove the client module and any docs/tests that reference it.
- Continue using direct `httpx` calls in repository-local scripts until the next adapter slice is ready.

## Open Questions

- Whether the first slice should immediately dogfood the client in `scripts/smoke_test.py` or keep that conversion for the next consumer-specific change.
- Whether the minimal exception surface should be one generic HTTP error type or a tiny hierarchy for common cases such as not found and validation failure.
