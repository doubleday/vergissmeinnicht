## MODIFIED Requirements

### Requirement: Environment-Driven Runtime Configuration
The system MUST load local runtime configuration for the API, database, vector store, and embedding-related settings from environment-backed configuration.

The environment-driven embedding settings MUST include the active embedding provider selection.

When the active provider supports model selection, the environment-driven embedding settings MUST also include the configured model identity and embedding dimensions for that runtime.

The documented local runtime configuration MUST make it possible to run the stack with the deterministic local embedder or with the supported local model-backed embedder without requiring source edits.

#### Scenario: Start the stack with configured connection settings
- **WHEN** a developer supplies the documented environment configuration for the local stack
- **THEN** `memory-api` uses that configuration to connect to PostgreSQL and Qdrant
- **AND** the stack starts without requiring source edits for local credentials or hostnames

#### Scenario: Start the stack with a configured deterministic embedder
- **WHEN** a developer supplies the documented environment configuration for the deterministic embedding provider
- **THEN** the local stack starts with that embedding runtime active
- **AND** the developer does not need to edit application source to select that runtime

#### Scenario: Start the stack with a configured local model-backed embedder
- **WHEN** a developer supplies the documented environment configuration for the supported local model-backed embedding runtime
- **THEN** the local stack starts with that embedding runtime active
- **AND** the developer does not need to edit application source to select the model or vector dimensions for that runtime
