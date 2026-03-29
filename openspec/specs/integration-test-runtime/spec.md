## Purpose

Define the reusable local runtime workflow for isolated integration tests, including setup, reset, run, and cleanup operations.

## Requirements

### Requirement: Integration Test Runtime Supports Explicit Lifecycle Operations

The system MUST provide a reusable local integration-test runtime with explicit lifecycle operations for setup, startup, reset, test execution, and cleanup.

#### Scenario: First-time setup prepares reusable integration runtime

- **WHEN** a developer prepares the integration-test runtime for first use
- **THEN** the system builds or initializes the required runtime resources
- **AND** the resulting runtime can be reused by later integration runs without creating a newly named project by default

#### Scenario: Repeated integration runs reuse existing runtime

- **WHEN** a developer runs the integration workflow repeatedly without changing the runtime definition
- **THEN** the system reuses the existing integration-test runtime resources
- **AND** the workflow does not require rebuilding a fresh project-specific image set for each ordinary local run

### Requirement: Integration Test Runtime Supports Deterministic Reset

The reusable integration-test runtime MUST provide a reset operation that restores the runtime to a clean deterministic starting state before tests run.

#### Scenario: Reset restores clean integration state without rebuild

- **WHEN** a developer requests integration runtime reset
- **THEN** the workflow restores a clean PostgreSQL and Qdrant test state for the next run
- **AND** it does not require rebuilding the runtime images if the runtime definition has not changed

### Requirement: Integration Test Runtime Supports Cleanup

The reusable integration-test runtime MUST support cleanup that removes the resources created for local integration verification.

#### Scenario: Cleanup removes integration runtime resources

- **WHEN** a developer requests integration-test cleanup
- **THEN** the workflow removes the reusable integration runtime resources it created
- **AND** later integration use can recreate them through the documented setup path
