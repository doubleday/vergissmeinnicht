## Purpose

Define the stable v1 contract for the core memory service API, including the canonical memory model and the four public operations for create, search, fetch, and archive.
## Requirements
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
- `source`: an object with a required normalized `type` string and an optional normalized `name` string
- `confidence`: a numeric confidence value from `0.0` to `1.0`
- `metadata`: a free-form object for client-supplied structured metadata
- `supersedes_memory_id`: an optional identifier of an earlier memory explicitly superseded by this memory
- `created_at`: the creation timestamp
- `updated_at`: the most recent mutation timestamp
- `last_accessed_at`: the most recent observed access timestamp
- `archived`: a lifecycle flag indicating whether the memory is archived

Canonical source normalization MUST be deterministic:

- `source.type` MUST treat leading and trailing whitespace as non-meaningful
- `source.type` MUST be returned in lowercase canonical form
- `source.name`, when present, MUST treat leading and trailing whitespace as non-meaningful
- `source.name` MUST be omitted from the canonical record when its normalized value would be empty

#### Scenario: Return a canonical memory record after create

- **WHEN** a client submits a valid create-memory request
- **THEN** the system returns the created memory in the canonical representation
- **AND** the response includes a service-generated `id`
- **AND** the response includes `source.type` in normalized canonical form
- **AND** the response includes `source.name` only when a non-empty normalized name was provided
- **AND** the response includes `supersedes_memory_id`, `created_at`, `updated_at`, `last_accessed_at`, and `archived`

#### Scenario: Return the same canonical source shape across endpoints

- **WHEN** a client creates, fetches, searches, or archives a memory
- **THEN** each returned canonical memory record includes the same normalized `source` shape for that stored memory
- **AND** the record does not require endpoint-specific source interpretation

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

The create operation MUST incorporate duplicate checks defined by the duplicate-write requirements before inserting a new active memory.

The create operation MUST accept an optional `supersedes_memory_id` that explicitly links the new memory to an existing memory in the same namespace.

The create operation MUST normalize the stored canonical `source` envelope before persistence.

#### Scenario: Create a valid memory

- **WHEN** a client submits a valid create-memory request with an allowed `kind`, `scope`, `namespace`, `title`, and `content`
- **THEN** the system stores a canonical memory record with a stable identifier and timestamps
- **AND** the stored record preserves any provided `tags`, normalized `source.type`, normalized `source.name`, `confidence`, `metadata`, and `supersedes_memory_id`
- **AND** the created record is marked `archived: false`
- **AND** the created memory is available for later fetch and search operations

#### Scenario: Omit a blank source name from the stored record

- **WHEN** a client submits a valid create-memory request whose `source.name` is absent or normalizes to an empty string
- **THEN** the system stores the canonical memory record without `source.name`
- **AND** later fetch, search, and archive responses omit `source.name` for that memory

#### Scenario: Create a memory that explicitly supersedes an earlier memory

- **WHEN** a client submits a valid create-memory request with `supersedes_memory_id` set to an existing memory in the same namespace
- **THEN** the system stores the new canonical memory record with that `supersedes_memory_id`
- **AND** the superseded memory remains independently fetchable and searchable unless a separate archive action changes its lifecycle state

#### Scenario: Return an existing record for an equivalent active write

- **WHEN** a client submits a valid create-memory request that is equivalent to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves the existing record's stable identifier and lifecycle fields
- **AND** the response preserves the stored record's normalized canonical `source` shape
- **AND** no additional active record is inserted

#### Scenario: Reject an invalid supersession reference

- **WHEN** a client submits a create-memory request with `supersedes_memory_id` that does not identify an existing memory in the same namespace
- **THEN** the system rejects the request with a validation error
- **AND** no partial memory record is created

#### Scenario: Reject an invalid confidence value

- **WHEN** a client submits a create-memory request with `confidence` outside the inclusive range `0.0` to `1.0`
- **THEN** the system rejects the request with a validation error

#### Scenario: Reject an invalid source payload

- **WHEN** a client submits a create-memory request without `source.type`
- **THEN** the system rejects the request with a validation error

### Requirement: Confidence Is Canonicalized Deterministically

The canonical memory record MUST store `confidence` in a deterministic normalized form.

For this slice, confidence normalization MUST:

- preserve the existing inclusive valid range of `0.0` to `1.0`
- round to exactly three decimal places using deterministic decimal rounding
- apply before persistence when a valid create-memory request produces a new canonical memory record

The system MUST return the stored normalized `confidence` value for that memory in create, fetch, search, and archive responses.

#### Scenario: Normalize an in-range confidence value before storing it

- **WHEN** a client submits a valid create-memory request with `confidence` containing more than three decimal places
- **THEN** the system stores the memory with `confidence` rounded to the canonical three-decimal representation
- **AND** the create response returns that normalized stored value

#### Scenario: Preserve canonical confidence across endpoints

- **WHEN** a memory has been stored with normalized `confidence`
- **THEN** fetch, search, and archive responses for that memory return the same normalized `confidence` value
- **AND** endpoint-specific confidence interpretation is not required

#### Scenario: Return the existing stored confidence for a duplicate create

- **WHEN** a client submits a create-memory request that resolves to an existing active memory under the duplicate-write rule
- **THEN** the system returns the existing canonical memory record
- **AND** the response preserves that stored record's normalized `confidence` value

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

### Requirement: Prevent Duplicate Active Memory Writes

The system MUST prevent duplicate create requests from producing multiple active canonical memory records when the requests are equivalent within the same namespace.

For this change, two create requests are equivalent when they have the same `namespace`, `scope`, `kind`, normalized `title`, normalized `content`, and the same `supersedes_memory_id` value.

Normalization for duplicate checks MUST be deterministic and MUST treat differences in leading or trailing whitespace as non-meaningful.

#### Scenario: Return the existing active memory for a duplicate create

- **WHEN** a client submits a create-memory request that is equivalent to an existing active memory in the same namespace
- **THEN** the system returns the existing active canonical memory record
- **AND** the system does not create an additional active canonical record for that request

#### Scenario: Create a new memory when no active duplicate exists

- **WHEN** a client submits a valid create-memory request and no equivalent active memory exists in the same namespace
- **THEN** the system creates a new canonical memory record
- **AND** the returned record is available for later fetch and search operations

#### Scenario: Create a new memory when supersession intent differs

- **WHEN** a client submits a valid create-memory request that matches an existing active memory on `namespace`, `scope`, `kind`, normalized `title`, and normalized `content` but has a different `supersedes_memory_id`
- **THEN** the request is not treated as an equivalent duplicate
- **AND** the system creates a distinct canonical memory record for that lineage

#### Scenario: Ignore archived memories for duplicate blocking

- **WHEN** a client submits a valid create-memory request that matches only archived memories
- **THEN** the system creates a new active canonical memory record
- **AND** archived records remain preserved for auditability

### Requirement: Search Stored Memories

The system MUST provide a search operation that returns relevant memories and accepts filter inputs that constrain the search scope.

When a query is present, the system MUST use semantic retrieval to obtain candidate memories before applying canonical search filters.

When no query is present, the system MUST preserve browse-style search behavior without requiring semantic retrieval.

The system MUST apply namespace, scope, kind, tag, archived, and superseded filtering rules against canonical stored memory records before returning results.

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

#### Scenario: Query-present search can return a semantic match without a direct substring hit

- **WHEN** a client searches with non-empty query text
- **AND** a stored memory is semantically relevant even though its title and content do not contain the exact query substring
- **THEN** that memory remains eligible for results through semantic retrieval
- **AND** the response returns the canonical stored memory record rather than a retrieval payload projection

#### Scenario: PostgreSQL filters still constrain semantic candidates

- **WHEN** semantic retrieval returns candidate memories from multiple namespaces, scopes, kinds, tags, or lifecycle states
- **THEN** the search response includes only candidates that satisfy the explicit request filters and current archived and superseded rules

#### Scenario: Query-less search remains browse-style

- **WHEN** a client searches without query text
- **THEN** the system does not require semantic retrieval to produce results
- **AND** the response preserves the existing browse-style search behavior

### Requirement: Search Uses Deterministic Query-Aware Ordering

The search operation MUST return results in a deterministic order.

When a query is present, the system MUST use semantic retrieval rank as the primary ordering signal for eligible candidates.

When multiple eligible results share the same semantic rank, the system MUST break ties by `updated_at` descending and then `id` ascending.

When no query is present, the system MUST preserve browse-style ordering by `updated_at` descending and `id` ascending.

#### Scenario: Higher-ranked semantic candidate appears first

- **WHEN** a client searches with query text and semantic retrieval returns two eligible candidate memories in a ranked order
- **THEN** the higher-ranked candidate appears earlier in the returned results

#### Scenario: PostgreSQL filters do not reorder surviving semantic candidates

- **WHEN** a client searches with query text
- **AND** some earlier semantic candidates are removed by namespace, tag, archived, or superseded filtering
- **THEN** the remaining eligible candidates preserve their relative semantic order in the final response

#### Scenario: Deterministic tie-breaking applies within the same semantic rank

- **WHEN** multiple eligible memories share the same semantic retrieval rank
- **THEN** the system orders those memories by `updated_at` descending
- **AND** uses `id` ascending to break any remaining ties deterministically

#### Scenario: Non-query searches stay chronological with deterministic ties

- **WHEN** a client searches without query text
- **THEN** the system orders matching memories by `updated_at` descending
- **AND** uses `id` ascending to break ties deterministically

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

### Requirement: Search Can Exclude Superseded Memories

The search operation MUST accept an optional `exclude_superseded` flag.

When `exclude_superseded` is `true`, the system MUST exclude any memory that is explicitly superseded by another active memory in the same namespace.

When `exclude_superseded` is `false` or omitted, the system MUST preserve the existing search behavior and keep superseded memories eligible for results.

#### Scenario: Preserve existing search behavior by default

- **WHEN** a client searches without setting `exclude_superseded`
- **THEN** memories remain eligible for results regardless of whether another memory explicitly supersedes them

#### Scenario: Exclude a superseded memory when requested

- **WHEN** a client searches with `exclude_superseded` set to `true`
- **THEN** the system excludes any matching memory whose identifier appears as `supersedes_memory_id` on another active memory in the same namespace
- **AND** matching memories that are not superseded by an active memory remain eligible for results

#### Scenario: Keep archived superseders from suppressing older memories

- **WHEN** a memory is superseded only by archived memories in the same namespace
- **AND** a client searches with `exclude_superseded` set to `true`
- **THEN** the older memory remains eligible for search results unless it is separately filtered out for another reason

### Requirement: Archive Does Not Cascade Across Supersession Links

The archive operation MUST remain record-local even when the targeted memory participates in a supersession link.

Archiving a memory MUST NOT archive, restore, or otherwise mutate any related superseding or superseded memories.

Archiving a memory MUST NOT rewrite or remove any stored `supersedes_memory_id` values.

#### Scenario: Archive a superseding memory without cascading

- **WHEN** a client archives a memory that explicitly supersedes another memory
- **THEN** only the targeted memory changes archived state
- **AND** the related older memory remains unchanged

#### Scenario: Archive a superseded memory without cascading

- **WHEN** a client archives a memory that is explicitly superseded by another memory
- **THEN** only the targeted memory changes archived state
- **AND** the related newer memory remains unchanged
