## ADDED Requirements

### Requirement: Disposable Integration Test Stack
The system MUST provide a Docker-based integration test workflow that starts `memory-api`, PostgreSQL, and Qdrant in an isolated test environment for each run.

The integration workflow MUST create and destroy its own runtime resources for that run.

#### Scenario: Start an isolated integration environment
- **WHEN** a developer or automation invokes the documented integration test entry point
- **THEN** the system starts `memory-api`, PostgreSQL, and Qdrant for that integration run
- **AND** the integration run does not require the developer's default local stack to already be running

#### Scenario: Tear down integration resources after the run
- **WHEN** the integration test run completes or is aborted
- **THEN** the system removes the integration run's containers, networks, and disposable storage resources
- **AND** a later integration run starts from a clean environment

### Requirement: Isolation From Default Local Development Resources
The integration test workflow MUST remain isolated from the default local development stack.

The integration workflow MUST NOT require reuse of the default host ports, default persistent Docker volumes, or previously persisted local development data.

#### Scenario: Run integration tests while the default local stack is absent
- **WHEN** a developer runs the integration test workflow on a machine without the default local stack running
- **THEN** the integration workflow completes using only its own test environment

#### Scenario: Avoid default persistent storage reuse
- **WHEN** the integration workflow writes PostgreSQL rows or Qdrant data during a run
- **THEN** those writes are stored only in the run's disposable test resources
- **AND** the workflow does not depend on or mutate the default development persistence resources

### Requirement: Real Service-Boundary Verification
The integration workflow MUST verify the live HTTP API against real PostgreSQL and Qdrant dependencies.

The integration workflow MUST exercise the same external API contract used by clients rather than calling internal service classes directly.

#### Scenario: Verify readiness and core lifecycle operations
- **WHEN** the integration workflow runs against its isolated test environment
- **THEN** it verifies that the API reports ready only after its dependencies are reachable
- **AND** it verifies successful create, fetch, search, and archive operations through the HTTP API

#### Scenario: Verify retrieval-backed search behavior through the live stack
- **WHEN** the integration workflow creates test memories and performs a query through the HTTP API
- **THEN** the workflow verifies that the returned search results include the expected memory records from the live stack

### Requirement: Internal-Network Test Execution
The integration test workflow MUST support executing its assertions without requiring the default API host port on the developer machine.

#### Scenario: Run tests without binding the default API host port
- **WHEN** the integration workflow executes its test assertions
- **THEN** the assertions can reach `memory-api` through the integration environment's internal runtime network
- **AND** the workflow does not require exclusive access to the default host port used by local development

### Requirement: Documented Verification Paths
The project MUST document the difference between unit tests, isolated integration tests, and manual smoke verification.

#### Scenario: Choose the appropriate verification path
- **WHEN** a developer reads the project verification documentation
- **THEN** the documentation identifies which command runs fast unit tests
- **AND** the documentation identifies which command runs isolated integration tests
- **AND** the documentation explains whether manual smoke verification remains available and when to use it
