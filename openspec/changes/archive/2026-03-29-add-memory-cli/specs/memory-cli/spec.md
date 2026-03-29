## ADDED Requirements

### Requirement: Typed CLI Covers The Four Stable Memory Operations
The system MUST provide a CLI that exposes the existing four public memory API operations without expanding the public contract.

The CLI MUST provide commands corresponding to:

- `POST /memories`
- `POST /memories/search`
- `GET /memories/{id}`
- `POST /memories/{id}/archive`

The CLI MUST construct typed request data aligned to the canonical memory API contract and MUST render typed canonical responses.

#### Scenario: Create a memory through the CLI
- **WHEN** a caller invokes the CLI with valid create-memory arguments
- **THEN** the CLI constructs the typed create request
- **AND** the CLI sends that request through the shared Python client to `POST /memories`
- **AND** the CLI renders the created canonical memory record

#### Scenario: Search memories through the CLI
- **WHEN** a caller invokes the CLI with valid search arguments
- **THEN** the CLI constructs the typed search request
- **AND** the CLI sends that request through the shared Python client to `POST /memories/search`
- **AND** the CLI renders the typed search response containing canonical memory records

#### Scenario: Fetch and archive through the CLI
- **WHEN** a caller invokes the CLI to fetch by id or archive by id
- **THEN** the CLI sends the request through the shared Python client to the corresponding existing endpoint
- **AND** the CLI renders the typed canonical memory record returned by that endpoint

### Requirement: CLI Stays Thin And Client-Backed
The CLI MUST remain a thin adapter over the existing shared Python client.

The CLI MUST support base URL and timeout configuration needed to target a running memory API instance.

The CLI MUST NOT introduce raw-HTTP code paths that bypass the shared Python client for the four stable memory operations.

The CLI MUST NOT introduce MCP-specific abstractions, new backend behavior, or workflow-specific helper commands in this slice.

#### Scenario: Target a non-default API location from the CLI
- **WHEN** a caller invokes the CLI with a non-default base URL or timeout configuration
- **THEN** the CLI initializes the shared Python client with that configuration
- **AND** subsequent CLI operations target that configured API location

#### Scenario: Keep the CLI within the existing adapter boundary
- **WHEN** a caller uses any of the four CLI commands
- **THEN** the CLI fulfills the command by calling the corresponding shared Python client operation
- **AND** the CLI does not require new backend endpoints or adapter-specific service behavior

### Requirement: CLI Reports Failures Predictably
The CLI MUST translate local validation failures, client transport failures, and API response failures into predictable CLI-visible failures.

The CLI-visible failure behavior MUST preserve enough information for a caller to distinguish malformed local input, an unreachable service, and a non-success API response.

#### Scenario: Surface local validation failure before request dispatch
- **WHEN** a caller provides invalid command arguments that cannot be converted into the typed request model
- **THEN** the CLI exits with a non-zero status
- **AND** the CLI reports the validation failure without requiring a successful API response

#### Scenario: Surface an API validation failure through the CLI
- **WHEN** the shared Python client reports a non-success API response for a CLI operation
- **THEN** the CLI exits with a non-zero status
- **AND** the CLI reports the API failure in a predictable form that preserves HTTP status information

#### Scenario: Surface a transport failure through the CLI
- **WHEN** the shared Python client cannot reach the memory API for a CLI operation
- **THEN** the CLI exits with a non-zero status
- **AND** the caller can distinguish that transport failure from an API response failure
