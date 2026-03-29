## Context

Milestone D is now split into three adapter layers: shared Python client, CLI, and MCP. The Python client slice is complete and already establishes the narrow reusable HTTP boundary. The next question is which consumer should prove that boundary first.

The CLI is the smaller next slice. It can stay inside the current Python package, reuse the existing typed models and `MemoryApiClient`, and expose immediate value for manual inspection and debugging. An MCP wrapper would add a second adaptation problem at the same time: protocol mapping, tool schema design, and host integration behavior. That makes MCP a larger slice even if it still reuses the same client.

## Goals / Non-Goals

**Goals:**

- Add a thin CLI over the existing Python client for create, search, fetch, and archive.
- Keep the CLI typed by mapping arguments directly into the existing Pydantic request models.
- Preserve the current four-endpoint API boundary with no new backend behavior.
- Return structured output suitable for manual inspection and shell use.
- Keep the slice independent from MCP so the adapter boundary remains easy to verify.

**Non-Goals:**

- Add MCP in the same slice.
- Add readiness, health, retries, collection management, or other non-memory commands.
- Introduce a richer workflow DSL or interactive TUI behavior.
- Add new backend contract fields, endpoints, or semantics.
- Bypass the shared client with raw HTTP calls from the CLI.

## Decisions

### Build the CLI as a thin wrapper around `MemoryApiClient`

Each CLI command should do only four things:

1. Parse command-line inputs.
2. Construct the existing typed request model when needed.
3. Call the corresponding `MemoryApiClient` method.
4. Render the typed response to stdout in a predictable serialized form.

Rationale:

- This directly validates that the shared client is sufficient for the next adapter.
- It prevents HTTP wiring, serialization logic, and response parsing from being duplicated again.
- It keeps future MCP work focused on protocol mapping rather than rebuilding transport behavior.

Alternatives considered:

- Build the CLI directly on `httpx`. Rejected because it would duplicate logic the client slice just centralized.
- Skip CLI and build MCP next. Rejected because MCP introduces a larger protocol boundary and more nonessential decisions for the next smallest slice.

### Keep the command surface aligned one-to-one with the four stable operations

The first CLI should expose only commands that correspond directly to the four stable memory operations: create, search, get by id, and archive.

Rationale:

- This preserves the exact public contract already documented in the service and client specs.
- It avoids inventing command-oriented workflows that would blur the adapter boundary.
- It keeps documentation and testing small.

Alternatives considered:

- Add convenience commands such as `list`, `remember`, or `ready`. Rejected because they either imply new backend behavior or introduce adapter-specific policy that is not required by this slice.

### Keep CLI input typed and explicit

The CLI should map user-provided flags and arguments into the existing typed models rather than accepting opaque JSON blobs as the primary interface.

Rationale:

- The user constraint is to keep the CLI thin and typed.
- Typed flags make the CLI self-documenting and keep validation behavior aligned with the existing model layer.
- This makes it easier to spot where validation happens: local model validation first, API validation second.

Alternatives considered:

- Accept only raw JSON payloads. Rejected because it weakens the typed adapter goal and mostly re-exposes the HTTP payload shape without CLI ergonomics.
- Add both typed flags and JSON input modes in the first slice. Rejected because it broadens scope before the minimal interface is proven.

### Emit structured output and predictable failure signaling

Successful commands should print structured serialized responses. Client transport failures and API response failures should be translated into stable CLI-visible failure behavior so shell users can distinguish malformed input, unreachable service, and API-level rejection.

Rationale:

- Manual inspection and debugging require output that is easy to read and pipe.
- The client already separates transport and response failures, so the CLI should preserve that distinction rather than collapsing it.
- This keeps the CLI usable in both human and scripted workflows without introducing extra backend semantics.

Alternatives considered:

- Use human-only prose output. Rejected because it is harder to compose and less suitable for debugging.
- Mirror raw tracebacks by default. Rejected because it leaks implementation detail and makes failure handling less predictable.

## Risks / Trade-offs

- [Typed CLI flags for nested fields such as `source` and repeated `tags` can become awkward] -> Mitigation: keep the first command surface explicit but minimal, and use direct flag-to-model mapping rather than adding a richer input format now.
- [Structured output choices can accidentally become a long-term UX contract] -> Mitigation: keep the initial output boring and aligned with serialized canonical models.
- [CLI-specific validation may duplicate some API validation] -> Mitigation: rely on existing Pydantic models for local validation and avoid new validation rules beyond argument parsing.
- [Deferring MCP means Milestone D still has one adapter remaining] -> Mitigation: use the CLI slice to prove the shared client seam first, reducing uncertainty before MCP.

## Migration Plan

1. Add a CLI entrypoint inside the existing Python package.
2. Implement one command per stable memory operation using the shared typed client.
3. Add tests for argument parsing, request mapping, success output, and failure behavior.
4. Document the CLI as the second Milestone D adapter slice and manual inspection tool.
5. Leave MCP for a subsequent change that consumes the same client boundary.

Rollback:

- Remove the CLI module, entrypoint, docs, and tests.
- Continue using ad hoc scripts or direct client usage for manual inspection until the next adapter slice is ready.

## Open Questions

- Whether the first CLI should default to JSON output only or allow a second human-readable format later.
- Whether the command name should live under the main project package name or a more direct `memory-*` entrypoint.
