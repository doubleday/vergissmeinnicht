## Why

The project currently has unit coverage for service logic and a manual smoke script for the live stack, but it does not have an automated integration test workflow that exercises the real API, PostgreSQL, and Qdrant together. This gap matters now because more behavior is crossing service boundaries, and verification must not depend on or mutate a developer's long-lived local stack.

## What Changes

- Add an isolated Docker-based integration test workflow that boots disposable `memory-api`, `postgres`, and `qdrant` services for test runs.
- Add automated integration coverage for core API flows such as readiness, create, fetch, search, and archive against real backing services.
- Define isolation requirements so integration runs do not reuse the default local development ports, volumes, or persistent data.
- Document how to run the integration suite locally and how it relates to the existing unit tests and manual smoke verification.
- Non-goal: replace the existing local development stack or broaden the public memory API contract.

## Capabilities

### New Capabilities
- `isolated-integration-testing`: Automated verification of the live memory service stack using disposable Docker-managed dependencies that remain isolated from a developer's normal local environment.

### Modified Capabilities
- None.

## Impact

- Affects Docker Compose-based test orchestration and related local test documentation.
- Affects verification coverage for the FastAPI memory API and its PostgreSQL and Qdrant integrations.
- May reorganize or incorporate the current manual smoke verification flow in [`scripts/smoke_test.py`](/Users/daniel/Source/myprojects/ai/vergissmeinnicht/scripts/smoke_test.py).
