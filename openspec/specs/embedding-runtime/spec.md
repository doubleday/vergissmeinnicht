## Purpose

Define the embedding runtime contract for selecting, validating, and operating the active embedder used by the memory service.

## Requirements

### Requirement: Configurable Embedding Runtime Selection
The system MUST select the active embedding runtime from environment-backed configuration instead of hard-coding a single embedder implementation.

The embedding runtime MUST support `deterministic-local` and one local sentence-transformer-backed provider in this slice.

The configured local sentence-transformer-backed provider MUST support a configurable model name so later model changes do not require service-level refactoring.

#### Scenario: Start the service with deterministic embeddings
- **WHEN** the configured embedding provider is `deterministic-local`
- **THEN** the service starts with the deterministic embedder active
- **AND** memory writes and query-present searches use that configured embedder without requiring source edits

#### Scenario: Start the service with a local model-backed embedder
- **WHEN** the configured embedding provider selects the supported local sentence-transformer-backed runtime
- **AND** the configured model and runtime settings are valid
- **THEN** the service starts with that local embedder active
- **AND** memory writes and query-present searches use that configured embedder without requiring source edits

### Requirement: Startup Fails For Invalid Embedding Runtime Configuration
The system MUST reject invalid embedding-runtime configuration during startup rather than waiting for the first memory write or search request to fail.

Invalid embedding-runtime configuration in this slice includes:

- an unsupported embedding provider value
- a local-provider configuration that cannot initialize the configured model
- an embedding-dimensions configuration that is incompatible with the active embedder output

#### Scenario: Reject an unsupported provider
- **WHEN** the service starts with an unsupported embedding provider value
- **THEN** startup fails with an observable configuration error
- **AND** the service does not advertise itself as ready

#### Scenario: Reject incompatible local embedding settings
- **WHEN** the service starts with the supported local provider selected
- **AND** the configured model or embedding dimensions are incompatible with that runtime
- **THEN** startup fails with an observable configuration error
- **AND** the service does not wait until the first search request to surface the problem

### Requirement: Embedding Runtime Changes Are A Retrieval Index Boundary
The system MUST treat embedding-provider, model, or embedding-dimensions changes as a retrieval-index compatibility boundary for the local runtime.

The project MUST document that a developer changing embedding provider, model, or vector dimensions needs a clean Qdrant collection or a separate collection name unless a separate migration workflow is used.

#### Scenario: Document a clean collection expectation for runtime changes
- **WHEN** a developer follows the documented local or retrieval-eval setup for a changed embedding provider, model, or vector size
- **THEN** the documentation instructs the developer to use a clean or separate Qdrant collection for that runtime
- **AND** the documented workflow does not imply that mixed old and new vectors are a supported steady-state configuration
