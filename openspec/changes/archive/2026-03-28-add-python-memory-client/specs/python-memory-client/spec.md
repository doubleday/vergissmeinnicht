## ADDED Requirements

### Requirement: Typed Python Client Covers The Four Stable Memory Operations
The system MUST provide a Python client that exposes the existing four public memory API operations without expanding the public contract.

The client MUST provide typed operations corresponding to:

- `POST /memories`
- `POST /memories/search`
- `GET /memories/{id}`
- `POST /memories/{id}/archive`

The client MUST accept and return typed request and response data aligned to the canonical memory API contract.

#### Scenario: Create a memory through the client
- **WHEN** a caller submits a valid create-memory payload through the Python client
- **THEN** the client sends the request to `POST /memories`
- **AND** the client returns the created canonical memory record in typed form

#### Scenario: Search memories through the client
- **WHEN** a caller submits a valid search payload through the Python client
- **THEN** the client sends the request to `POST /memories/search`
- **AND** the client returns the typed search response containing canonical memory records

#### Scenario: Fetch and archive through the client
- **WHEN** a caller requests fetch-by-id or archive through the Python client
- **THEN** the client sends the request to the corresponding existing endpoint
- **AND** the client returns the typed canonical memory record from that endpoint

### Requirement: Client Configuration Stays Narrow And Adapter-Friendly
The Python client MUST support only the configuration needed to call the existing memory API predictably from other adapters in this slice.

The client MUST support a configurable base URL.

The client MUST support timeout configuration and an injectable HTTP transport or client seam suitable for tests and later adapter composition.

The client MUST NOT require a CLI-specific, MCP-specific, or workflow-specific abstraction layer.

#### Scenario: Configure the client for a non-default runtime location
- **WHEN** a caller initializes the Python client with a non-default base URL
- **THEN** subsequent client operations target that configured API location

#### Scenario: Inject a transport seam for verification
- **WHEN** a caller initializes the Python client with a test or custom HTTP transport seam
- **THEN** the client uses that seam for subsequent API calls
- **AND** the caller does not need a live service process to verify client request and response behavior

### Requirement: Client Reports HTTP Failures Predictably
The Python client MUST translate non-success HTTP responses from the memory API into predictable client-visible failures.

The client-visible failure MUST preserve enough information for a higher-level adapter to distinguish API failures from local transport failures.

#### Scenario: Surface an API validation failure
- **WHEN** the memory API returns a non-success validation response for a client operation
- **THEN** the Python client raises a predictable client-visible API failure
- **AND** the failure preserves the HTTP status information needed by the caller

#### Scenario: Surface a missing-memory failure
- **WHEN** the memory API returns a not-found response for fetch or archive
- **THEN** the Python client raises a predictable client-visible API failure
- **AND** the caller can distinguish that API response from a local transport error
