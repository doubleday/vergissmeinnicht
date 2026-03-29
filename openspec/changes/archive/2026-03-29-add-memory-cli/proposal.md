## Why

Milestone D still needs user-facing adapters on top of the shared Python client. The smallest useful next slice is a thin CLI that proves the client can support manual inspection and debugging without adding any new backend behavior or mixing MCP concerns into the same change.

The repository already has a narrow typed client for the four stable memory endpoints. A CLI can now reuse that client directly and provide a practical operator entry point with less protocol surface and less implementation risk than an MCP wrapper.

## What Changes

- Add a thin typed CLI over the existing Python client for the four stable memory operations: create, search, fetch, and archive.
- Keep the CLI boundary limited to argument parsing, typed request construction, client invocation, and structured output.
- Define predictable CLI-visible handling for client response failures and transport failures without changing backend behavior.
- Document and verify the CLI as the next Milestone D adapter slice.
- Non-goal: add MCP, add new backend endpoints, add readiness or workflow commands, or introduce adapter-specific memory behavior in this slice.

## Capabilities

### New Capabilities
- `memory-cli`: A thin typed CLI for the four stable memory API operations.

### Modified Capabilities
- None.

## Impact

- Affects the installed package surface, command-line entrypoint configuration, and adapter-facing documentation.
- Adds tests for CLI argument handling, typed request mapping, output behavior, and client error presentation.
- Exercises the shared Python client as the only HTTP boundary for a user-facing adapter.
- Does not change the public memory API endpoints, canonical memory contract, or backend persistence behavior.
