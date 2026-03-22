## Context

The repository currently separates fast unit coverage in `tests/` from a manual end-to-end verification script in `scripts/smoke_test.py`. The manual script talks to the default local stack through `http://127.0.0.1:8000`, and the default [`docker-compose.yml`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/docker-compose.yml) binds fixed host ports and persistent named volumes for PostgreSQL and Qdrant. That setup is appropriate for development, but it is not appropriate for automated integration runs because the tests would either require the default stack to be running or risk reusing the same ports, volumes, and persisted data.

This change needs a test workflow that verifies the real FastAPI, PostgreSQL, and Qdrant integration while remaining disposable and isolated from the normal developer environment. The design must stay container-first and boring: reuse the existing stack shape, avoid introducing a new orchestration framework, and keep the current public API unchanged.

## Goals / Non-Goals

**Goals:**
- Provide an automated integration test workflow that exercises `memory-api`, PostgreSQL, and Qdrant together.
- Ensure each integration run uses disposable infrastructure that does not reuse the default development ports, volumes, or persistent data.
- Cover the core observable flows needed for confidence at service boundaries: readiness, create, fetch, search, archive, and selected restart behavior.
- Keep the workflow compatible with local execution and straightforward to adopt in CI later.

**Non-Goals:**
- Replace the existing developer-focused local Compose stack.
- Redesign the application API, persistence model, or embedding behavior.
- Introduce a general-purpose test orchestration framework beyond Docker Compose and the current Python test tooling.
- Convert every existing unit test into an integration test or require integration tests on every inner-loop edit.

## Decisions

### Use a dedicated integration Compose overlay rather than the default development Compose file alone

Integration runs will use the existing Compose stack as a base plus an integration-specific overlay that changes the runtime shape for tests. The overlay will define disposable infrastructure behavior without changing the developer-oriented defaults in the main Compose file.

Rationale:
- The current base Compose file intentionally exposes fixed ports and persistent named volumes for local inspection and reuse.
- Integration tests need the opposite defaults: isolation and deterministic teardown.
- An overlay keeps shared service definitions aligned while allowing test-specific overrides such as ephemeral volumes, internal-only networking, and a test-runner service.

Alternatives considered:
- Reuse only the base Compose file with environment-variable overrides. Rejected because it makes the isolation contract fragile and easy to bypass accidentally.
- Introduce a separate Docker orchestration tool such as Testcontainers. Rejected for now because Compose already matches the project’s container-first workflow and keeps the implementation smaller.

### Run integration tests from a dedicated container on the Compose network

The integration suite will run from a `test-runner` container that depends on the application stack and calls the API over the internal Compose network using the service hostname. Tests will not require the API, PostgreSQL, or Qdrant to publish their default ports to the host.

Rationale:
- Internal networking avoids collisions with a developer’s normal local stack.
- Tests become portable between local and CI environments because they no longer depend on host port assumptions.
- The test runner can execute the same Python-based assertions already familiar in the repository.

Alternatives considered:
- Run the tests on the host and bind random host ports. Possible, but it still couples the test flow to host networking and complicates environment discovery.
- Point host-based tests at the normal `localhost:8000` stack. Rejected because it fails the isolation requirement.

### Treat isolation as a behavioral contract, not just a convenience

The integration workflow will explicitly require a unique Compose project scope and disposable storage for every run, with teardown that removes test-created containers, networks, and volumes. The tests may also use integration-specific namespaces or collection names, but those are defense-in-depth rather than the primary isolation boundary.

Rationale:
- Named persistent volumes are the largest risk for mutating a normal local environment.
- A unique Compose project plus `down -v` gives clear lifecycle ownership for test resources.
- Namespace-level isolation alone is insufficient because it does not protect against storage reuse or port collisions.

Alternatives considered:
- Rely only on unique memory namespaces inside the default stack. Rejected because it still mutates the same backing stores.
- Reuse persistent test volumes across runs for speed. Rejected because it weakens test determinism and blurs the isolation guarantee.

### Keep the existing smoke verification flow, but align it with the isolated integration workflow

The current smoke verification script or its logic can be reused as a building block, but the automated integration suite will become the primary repeatable verification mechanism. Any persistence-across-restart assertions should run inside the isolated integration environment instead of against the default local stack.

Rationale:
- The smoke script already expresses valuable end-to-end behavior.
- Reuse reduces duplicate verification logic.
- Moving restart assertions into the isolated workflow preserves the original confidence signal without risking shared local data.

Alternatives considered:
- Leave the smoke script completely separate and add a parallel integration suite with overlapping checks. Rejected because it creates avoidable duplication and drift.
- Replace the smoke script entirely. Rejected because the repository may still benefit from a simple manual verification entry point.

## Risks / Trade-offs

- [Compose overlay drift from the base stack] → Mitigation: keep the overlay narrowly focused on isolation and test execution, with shared service definitions inherited from the base file.
- [Integration tests become slow enough that developers avoid them] → Mitigation: keep the suite small and focused on boundary behavior, while preserving fast unit tests for inner-loop work.
- [Restart or persistence assertions become flaky under Docker startup timing] → Mitigation: rely on readiness checks and explicit wait logic rather than fixed sleeps.
- [A host-published port sneaks back into the integration path later] → Mitigation: define the spec so integration tests must succeed through the internal network without requiring the default host ports.
- [Reusing smoke-test logic could preserve assumptions tied to the default stack] → Mitigation: parameterize runtime endpoints and project-specific lifecycle commands so the logic can operate inside isolated test infrastructure.

## Migration Plan

1. Add the isolated integration capability spec to define the required behavior.
2. Introduce the integration Compose overlay, disposable lifecycle command, and test-runner wiring.
3. Port or add a small set of integration tests for the core API flows.
4. Update documentation to distinguish unit tests, integration tests, and manual smoke verification.
5. Optionally wire the same integration entry point into CI once the local flow is stable.

Rollback is straightforward because this change adds a separate test workflow. If issues arise, the integration-specific files can be removed without affecting the existing developer stack or public API.

## Open Questions

- Should restart verification restart only `memory-api`, or the full isolated stack, for the first iteration?
- Should the integration workflow be exposed primarily as a `docker compose ... up --exit-code-from test-runner` entry point, a small wrapper script, or both?
