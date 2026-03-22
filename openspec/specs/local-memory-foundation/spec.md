## Purpose

Define the local development foundation for the memory service stack, including one-command startup, persistent backing stores, environment-driven configuration, readiness checks, and direct inspection of canonical and retrieval-layer data.

## Requirements

### Requirement: One-Command Local Stack Startup
The system MUST provide a local development entry point that starts `memory-api`, `postgres`, and `qdrant` together with a single command.

#### Scenario: Start the full local stack
- **WHEN** a developer runs the documented local startup command
- **THEN** the system starts containers for `memory-api`, `postgres`, and `qdrant`
- **AND** the services are connected through a shared local runtime configuration

### Requirement: Persistent Local Storage
The local stack MUST persist PostgreSQL and Qdrant data across container restarts.

#### Scenario: Restart the stack without losing state
- **WHEN** a developer stops and restarts the local stack after data has been written
- **THEN** previously stored PostgreSQL rows remain available after restart
- **AND** previously stored Qdrant collections and payloads remain available after restart

### Requirement: Environment-Driven Runtime Configuration
The system MUST load local runtime configuration for the API, database, vector store, and embedding-related settings from environment-backed configuration.

#### Scenario: Start the stack with configured connection settings
- **WHEN** a developer supplies the documented environment configuration for the local stack
- **THEN** `memory-api` uses that configuration to connect to PostgreSQL and Qdrant
- **AND** the stack starts without requiring source edits for local credentials or hostnames

### Requirement: Dependency-Aware Health Checks
The local stack MUST expose health or readiness checks that confirm the API process is running and can reach its required backing services.

#### Scenario: Confirm the API is ready for memory operations
- **WHEN** the API process has started and both PostgreSQL and Qdrant are reachable
- **THEN** the readiness check reports the API as ready

#### Scenario: Report a dependency failure during startup
- **WHEN** PostgreSQL or Qdrant is unavailable to the API
- **THEN** the readiness check reports the API as not ready
- **AND** the failure is observable without requiring application code inspection

### Requirement: Direct Inspection of Backing Stores
The local foundation MUST support direct inspection of canonical and retrieval-layer data during development.

#### Scenario: Inspect stored data in backing services
- **WHEN** a developer has written memory data through the API
- **THEN** the corresponding canonical records are inspectable in PostgreSQL
- **AND** the corresponding retrieval records are inspectable in Qdrant
