## ADDED Requirements

### Requirement: Track Last Memory Access Time

The system MUST track the most recent observed access time for each canonical memory record using `last_accessed_at`.

The canonical memory record MUST include `last_accessed_at` as a timestamp.

The system MUST initialize `last_accessed_at` when a new memory is created.

#### Scenario: Return `last_accessed_at` in the canonical record

- **WHEN** a client creates, fetches, searches, or archives a memory
- **THEN** the returned canonical memory representation includes `last_accessed_at`

#### Scenario: Initialize `last_accessed_at` at creation

- **WHEN** a client submits a valid create-memory request that produces a new canonical memory record
- **THEN** the system sets `last_accessed_at` on that new record
- **AND** the returned canonical memory includes the initialized timestamp

#### Scenario: Preserve `last_accessed_at` for duplicate create responses

- **WHEN** a client submits a create-memory request that resolves to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the duplicate-write response does not require advancing `last_accessed_at`

### Requirement: Advance Access Time on Read Operations

The system MUST advance `last_accessed_at` when an existing memory is successfully returned through the public read paths.

For this change, the public read paths are `GET /memories/{id}` and `POST /memories/search` for memories included in the response.

#### Scenario: Advance access time on fetch by id

- **WHEN** a client fetches an existing memory by identifier
- **THEN** the system advances that memory's `last_accessed_at`
- **AND** the returned canonical memory includes the updated access timestamp

#### Scenario: Advance access time for returned search results

- **WHEN** a client searches and the response includes one or more matching memories
- **THEN** the system advances `last_accessed_at` for each returned memory
- **AND** each returned canonical memory includes its updated access timestamp

#### Scenario: Do not update access time when a search returns no results

- **WHEN** a client searches and no memories are returned
- **THEN** the system does not update any stored `last_accessed_at` values

## MODIFIED Requirements

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
- `last_accessed_at`: the most recent observed access timestamp
- `archived`: a lifecycle flag indicating whether the memory is archived

#### Scenario: Return a canonical memory record after create

- **WHEN** a client submits a valid create-memory request
- **THEN** the system returns the created memory in the canonical representation
- **AND** the response includes a service-generated `id`
- **AND** the response includes `created_at`, `updated_at`, `last_accessed_at`, and `archived`

#### Scenario: Reject a create request missing canonical required fields

- **WHEN** a client submits a create-memory request without `kind`, `scope`, `namespace`, `title`, or `content`
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

### Requirement: Fetch a Memory by Identifier

The system MUST provide an operation that returns the canonical representation of a stored memory by identifier.

#### Scenario: Fetch an existing memory

- **WHEN** a client requests an existing memory identifier
- **THEN** the system returns the canonical memory record including lifecycle fields and metadata
- **AND** the returned record preserves the current archived state
- **AND** the returned record includes the updated `last_accessed_at` value for that fetch

#### Scenario: Fetch a missing memory

- **WHEN** a client requests a memory identifier that does not exist
- **THEN** the system returns a not-found response

### Requirement: Search Stored Memories

The system MUST provide a search operation that returns relevant non-archived memories and accepts filter inputs that constrain the search scope.

#### Scenario: Search with namespace and scope filters

- **WHEN** a client searches using query text plus namespace and scope filters
- **THEN** the system returns only memories matching the provided filters
- **AND** archived memories are excluded from results by default
- **AND** each returned memory includes an updated `last_accessed_at` value for that search response

#### Scenario: Search with archived memories explicitly included

- **WHEN** a client searches with an explicit request to include archived memories
- **THEN** the system may return both active and archived memories that match the query and filters
- **AND** each returned memory includes an updated `last_accessed_at` value for that search response

#### Scenario: Search an empty store

- **WHEN** a client searches before any memories have been stored
- **THEN** the system returns an empty result set without error

#### Scenario: Search contract does not expose retrieval internals

- **WHEN** a client performs a search
- **THEN** the system returns matching memories without requiring the client to know which storage or ranking mechanisms were used internally

### Requirement: Archive Without Deleting

The system MUST support archiving a memory without deleting its canonical history.

#### Scenario: Archive an existing memory

- **WHEN** a client archives an existing active memory
- **THEN** the system marks the memory as archived
- **AND** the system preserves the original identifier and canonical content
- **AND** the system updates the memory's lifecycle state for later fetch operations
- **AND** the archive response preserves the current `last_accessed_at` value unless a prior read in the same request path changed it
- **AND** subsequent default search results exclude that memory

#### Scenario: Archive a missing memory

- **WHEN** a client archives a memory identifier that does not exist
- **THEN** the system returns a not-found response
