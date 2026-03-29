## MODIFIED Requirements

### Requirement: Disposable Integration Test Stack

The system MUST provide a Docker-based integration test workflow that starts `memory-api`, PostgreSQL, and Qdrant in an isolated test environment.

The integration workflow MUST provide a documented way to restore a clean deterministic runtime state before a run.

The local workflow MAY satisfy this through a reusable isolated integration runtime rather than requiring a newly created project for every run.

#### Scenario: Start an isolated integration environment

- **WHEN** a developer or automation invokes the documented integration test entry point
- **THEN** the system starts `memory-api`, PostgreSQL, and Qdrant for that integration run
- **AND** the integration run does not require the developer's default local stack to already be running

#### Scenario: Restore clean deterministic state before a run

- **WHEN** the integration workflow prepares to execute tests
- **THEN** the workflow restores a clean deterministic runtime state for PostgreSQL and Qdrant
- **AND** the subsequent test run starts from that clean state

#### Scenario: Remove integration resources when requested

- **WHEN** the developer requests integration runtime cleanup
- **THEN** the system removes the integration runtime's containers, networks, and test storage resources
- **AND** a later integration run can recreate them through the documented setup path

### Requirement: Isolation From Default Local Development Resources

The integration test workflow MUST remain isolated from the default local development stack.

The integration workflow MUST NOT require reuse of the default host ports, default persistent Docker volumes, or previously persisted local development data.

#### Scenario: Run integration tests while the default local stack is absent

- **WHEN** a developer runs the integration test workflow on a machine without the default local stack running
- **THEN** the integration workflow completes using only its own test environment

#### Scenario: Avoid default persistent storage reuse

- **WHEN** the integration workflow writes PostgreSQL rows or Qdrant data during a run
- **THEN** those writes are stored only in the integration runtime's isolated test resources
- **AND** the workflow does not depend on or mutate the default development persistence resources
