## Context

The current integration workflow proves correctness against a live FastAPI, PostgreSQL, and Qdrant stack by creating a fresh timestamped Docker Compose project for each run. That gives deterministic initial state, but it also makes repeat verification slow because every run rebuilds project-specific images, recreates runtime resources, and pays Docker image export/unpack cost again.

The repository now has a reusable local retrieval-eval runtime, which shows that “isolated and deterministic” does not require “fresh project identity every run.” The same principle can be applied to integration tests if the workflow provides a trusted reset step that restores a known starting state before test execution.

## Goals / Non-Goals

**Goals:**
- Keep integration tests deterministic and isolated from the default local stack.
- Replace per-run project recreation with a reusable local integration runtime.
- Add explicit lifecycle operations for setup, start, reset, run, and cleanup.
- Preserve the current live HTTP API test boundary and smoke verification behavior.

**Non-Goals:**
- Changing API behavior or search semantics.
- Expanding the integration test suite beyond its current intent.
- Merging integration runtime with the retrieval-eval runtime.
- Introducing CI infrastructure changes in this slice.

## Decisions

### Use a fixed local integration Compose project

The integration workflow should use a stable local project identity and fixed image tags instead of timestamped per-run names.

Rationale:
- Stable names allow Docker to reuse images and service definitions between runs.
- This removes the repeated project-specific image churn that currently dominates wall-clock time.
- It keeps the runtime inspectable with normal Docker commands.

Alternative considered:
- Keep timestamped projects and rely on Docker cache alone. Rejected because cache helps only part of the cost; export/unpack and per-project tagging still dominate.

### Define determinism through reset, not through project replacement

The integration workflow should provide a trusted reset path that restores the runtime to a clean state before running tests.

Rationale:
- Deterministic tests need known data state, not necessarily new project identity.
- A reset step can recreate clean PostgreSQL and Qdrant state without rebuilding images.
- This preserves the isolation guarantees while materially improving repeat-run speed.

Alternative considered:
- Keep volume recreation implicit inside one monolithic run command. Rejected because explicit reset is easier to understand and easier to verify.

### Split lifecycle into setup, start, reset, run, and cleanup

The reusable integration runtime should expose explicit commands for its lifecycle, similar to the retrieval-eval runtime.

Rationale:
- First-time setup, repeated runs, and teardown are distinct operator needs.
- Explicit commands make the system behavior more transparent.
- This keeps rebuilds intentional instead of happening silently during ordinary test runs.

Alternative considered:
- Add flags to the existing integration script only. Rejected because subcommands communicate intent more clearly and fit the repo’s evolving runtime pattern.

### Keep integration runtime separate from default local and retrieval-eval runtimes

The new runtime should have its own Compose file or equivalent isolated configuration, volumes, and project name.

Rationale:
- Integration tests should not mutate the default development stack.
- Retrieval-eval state and integration-test state serve different purposes and should not be mixed.
- Separate runtimes make cleanup and troubleshooting clearer.

Alternative considered:
- Reuse the retrieval-eval runtime for integration tests. Rejected because it conflates two different workflows and state models.

## Risks / Trade-offs

- [Reset logic may be less obviously trustworthy than full stack recreation] -> Mitigation: make reset explicit, document it clearly, and ensure it recreates the full integration data state rather than partially mutating it.
- [A static integration runtime adds another local environment to manage] -> Mitigation: keep lifecycle commands small and consistent with the retrieval-eval runtime.
- [Long-lived images can still consume disk until cleaned up] -> Mitigation: provide a cleanup command that removes runtime resources and images intentionally.

## Migration Plan

1. Add a reusable integration runtime definition with fixed project and image names.
2. Implement lifecycle commands for setup, start, reset, run, and cleanup.
3. Update the integration workflow to reset to a clean state before test execution instead of relying on new project creation.
4. Update documentation to explain the new deterministic state model and when to reset versus rebuild.

Rollback is straightforward: the static runtime commands can be removed and the old disposable integration workflow restored if reset-driven determinism proves unreliable.

## Open Questions

- Should reset recreate volumes entirely, or should it use explicit database and collection reset commands inside the running services?
- Should the integration runtime and retrieval-eval runtime share helper scripts for lifecycle management, or stay separate for now?
