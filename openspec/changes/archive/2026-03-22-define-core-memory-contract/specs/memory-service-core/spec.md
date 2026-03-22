## ADDED Requirements

### Requirement: Canonical Memory Record Shape

The system MUST expose a canonical memory representation for create, fetch, search, and archive operations.

The canonical memory record MUST contain:

- `id`: a stable service-generated identifier
- `kind`: an allowed memory taxonomy value
- `scope`: an allowed scope taxonomy value
- `namespace`: a client-provided namespace string
- `title`: a short human-readable label
- `content`: the canonical memory text
- `tags`: a list of zero or more string tags
- `source`: an object that includes at least `type`
- `confidence`: a numeric confidence value from `0.0` to `1.0`
- `metadata`: a free-form object for client-supplied structured metadata
- `created_at`: the creation timestamp
- `updated_at`: the most recent mutation timestamp
- `archived`: a lifecycle flag indicating whether the memory is archived

#### Scenario: Return a canonical memory record after create

- **WHEN** a client submits a valid create-memory request
- **THEN** the system returns the created memory in the canonical representation
- **AND** the response includes a service-generated `id`
- **AND** the response includes `created_at`, `updated_at`, and `archived`

#### Scenario: Reject a create request missing canonical required fields

- **WHEN** a client submits a create-memory request without `kind`, `scope`, `namespace`, `title`, or `content`
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

### Requirement: Constrained Memory Taxonomy

The system MUST constrain the first public contract to a small taxonomy.

Allowed `kind` values in v1 are:

- `rule`
- `example`
- `feedback`
- `correction`
- `preference`

Allowed `scope` values in v1 are:

- `global`
- `project`
- `agent`

#### Scenario: Accept an allowed taxonomy combination

- **WHEN** a client submits a create-memory request with an allowed `kind` and `scope`
- **THEN** the system accepts the taxonomy values as valid input

#### Scenario: Reject an invalid taxonomy value

- **WHEN** a client submits a create-memory request with an unsupported memory kind or scope
- **THEN** the system rejects the request with a validation error

### Requirement: Stable v1 API Boundary

The system MUST keep the first public contract limited to four operations:

- `POST /memories`
- `POST /memories/search`
- `GET /memories/{id}`
- `POST /memories/{id}/archive`

The v1 contract MUST treat update-in-place, delete, bulk import, automatic extraction from conversations, and collection-management operations as out of scope.

#### Scenario: Complete the v1 lifecycle through four endpoints

- **WHEN** a client needs to create, search, fetch, and archive memories
- **THEN** the client can complete those actions using only the four v1 endpoints

#### Scenario: Exclude out-of-scope write operations from v1

- **WHEN** a client looks for delete or update endpoints in the v1 contract
- **THEN** the contract does not define those operations

### Requirement: Create Explicit Memories

The system MUST provide an API operation that creates a memory record from explicit client input and persists the canonical memory data for later retrieval.

#### Scenario: Create a valid memory

- **WHEN** a client submits a valid create-memory request with an allowed `kind`, `scope`, `namespace`, `title`, and `content`
- **THEN** the system stores a canonical memory record with a stable identifier and timestamps
- **AND** the stored record preserves any provided `tags`, `source.type`, `confidence`, and `metadata`
- **AND** the created record is marked `archived: false`
- **AND** the created memory is available for later fetch and search operations

#### Scenario: Reject an invalid confidence value

- **WHEN** a client submits a create-memory request with `confidence` outside the inclusive range `0.0` to `1.0`
- **THEN** the system rejects the request with a validation error

#### Scenario: Reject an invalid source payload

- **WHEN** a client submits a create-memory request without `source.type`
- **THEN** the system rejects the request with a validation error

### Requirement: Search Stored Memories

The system MUST provide a search operation that returns relevant non-archived memories and accepts filter inputs that constrain the search scope.

#### Scenario: Search with namespace and scope filters

- **WHEN** a client searches using query text plus namespace and scope filters
- **THEN** the system returns only memories matching the provided filters
- **AND** archived memories are excluded from results by default

#### Scenario: Search with archived memories explicitly included

- **WHEN** a client searches with an explicit request to include archived memories
- **THEN** the system may return both active and archived memories that match the query and filters

#### Scenario: Search an empty store

- **WHEN** a client searches before any memories have been stored
- **THEN** the system returns an empty result set without error

#### Scenario: Search contract does not expose retrieval internals

- **WHEN** a client performs a search
- **THEN** the system returns matching memories without requiring the client to know which storage or ranking mechanisms were used internally

### Requirement: Fetch a Memory by Identifier

The system MUST provide an operation that returns the canonical representation of a stored memory by identifier.

#### Scenario: Fetch an existing memory

- **WHEN** a client requests an existing memory identifier
- **THEN** the system returns the canonical memory record including lifecycle fields and metadata
- **AND** the returned record preserves the current archived state

#### Scenario: Fetch a missing memory

- **WHEN** a client requests a memory identifier that does not exist
- **THEN** the system returns a not-found response

### Requirement: Archive Without Deleting

The system MUST support archiving a memory without deleting its canonical history.

#### Scenario: Archive an existing memory

- **WHEN** a client archives an existing active memory
- **THEN** the system marks the memory as archived
- **AND** the system preserves the original identifier and canonical content
- **AND** the system updates the memory's lifecycle state for later fetch operations
- **AND** subsequent default search results exclude that memory

#### Scenario: Archive a missing memory

- **WHEN** a client archives a memory identifier that does not exist
- **THEN** the system returns a not-found response
