## Why

Milestone D is about shared adapters, and the narrowest useful adapter seam is a typed Python client over the existing HTTP contract. Building that first removes duplicated request wiring from later CLI and MCP work without expanding the public API beyond the current four memory operations.

## What Changes

- Add a thin Python client for the memory API that exposes typed create, search, fetch, and archive operations.
- Keep the client boundary aligned to the existing four public endpoints and canonical request/response shapes.
- Add a small transport/configuration seam so later adapters can provide base URL, timeout, and test transports without introducing a broader SDK abstraction.
- Define predictable client-side error handling for HTTP failure responses from the existing API.
- Document and verify the client as the first Milestone D adapter slice.
- Non-goal: add MCP, add a CLI, redesign the memory API, or introduce higher-level adapter workflows in this slice.

## Capabilities

### New Capabilities
- `python-memory-client`: A thin typed Python client for the four stable memory API operations.

### Modified Capabilities
- None.

## Impact

- Affects the installed Python package surface, adapter-facing HTTP integration code, and user documentation.
- Adds tests for client request serialization, response parsing, and error handling.
- Creates the shared Python boundary that later CLI and MCP adapters can build on.
- Does not change the public memory API endpoints, canonical memory contract, or backend persistence behavior.
