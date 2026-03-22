## Why

The project has a stable core API contract and a roadmap, but it still lacks a runnable local stack. Before client adapters or quality controls can be validated, the repository needs a one-command foundation that brings up the service, persists state, and makes the backing stores inspectable.

## What Changes

- Add a local development stack for `memory-api`, `postgres`, and `qdrant` using Docker Compose.
- Define environment configuration for database, vector store, and embedding-related settings required to boot the stack locally.
- Add basic service health and startup checks so developers can confirm the stack is ready before exercising the API.
- Establish the initial application wiring needed to connect the API service to PostgreSQL and Qdrant while keeping the existing core memory contract unchanged.
- Exclude shared adapters, memory hygiene controls, automatic extraction, and advanced ranking from this slice.

## Capabilities

### New Capabilities
- `local-memory-foundation`: Local bootstrap and operability requirements for starting, persisting, and inspecting the memory service stack.

### Modified Capabilities
- None.

## Impact

- Adds the first runnable application and infrastructure files in the repository
- Introduces Docker Compose, container configuration, and local environment settings
- Connects runtime infrastructure to the existing [`memory-service-core`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/openspec/specs/memory-service-core/spec.md) contract without changing its public requirements
- Creates a base that later implementation changes can extend for semantic search, adapters, and memory quality controls
