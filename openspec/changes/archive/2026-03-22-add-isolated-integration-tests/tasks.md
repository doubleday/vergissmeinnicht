## 1. Isolated test orchestration

- [x] 1.1 Add an integration-specific Docker Compose overlay or equivalent entry point that starts `memory-api`, PostgreSQL, and Qdrant as disposable test resources.
- [x] 1.2 Add a test-runner execution path that can reach `memory-api` over the integration environment's internal network without depending on the default host port bindings.
- [x] 1.3 Ensure the integration entry point uses per-run isolation and teardown so test-created containers, networks, and storage are removed after the run.

## 2. Live-stack integration coverage

- [x] 2.1 Add automated integration tests that verify readiness plus create, fetch, search, and archive flows through the live HTTP API.
- [x] 2.2 Add an integration assertion for retrieval-backed search against the real PostgreSQL and Qdrant-backed stack.
- [x] 2.3 Rework or incorporate the existing smoke verification logic so any restart or persistence checks run inside the isolated integration environment.

## 3. Verification documentation

- [x] 3.1 Document the command for fast unit tests, the command for isolated integration tests, and the role of any remaining manual smoke verification.
- [x] 3.2 Document the isolation guarantees for the integration workflow, including that it does not require the default local stack or reuse its persistent resources.
