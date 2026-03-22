## MODIFIED Requirements

### Requirement: Search Stored Memories

The system MUST provide a search operation that returns relevant memories and accepts filter inputs that constrain the search scope.

When a query is present, the system MUST attempt semantic retrieval to obtain candidate memories before applying canonical search filters.

When semantic retrieval yields one or more candidate memories, the system MUST use those candidates as the query-present search input before applying canonical search filters.

When semantic retrieval yields no candidate memories, the system MUST fall back to canonical PostgreSQL-backed lexical matching for that query-present request.

When semantic retrieval is temporarily unavailable for a query-present request, the system MUST fall back to canonical PostgreSQL-backed lexical matching for that request instead of failing the search operation solely because the retrieval index could not answer.

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

#### Scenario: Query-present search falls back when semantic retrieval returns no candidates

- **WHEN** a client searches with non-empty query text
- **AND** semantic retrieval returns no candidate memories
- **THEN** the system falls back to canonical PostgreSQL-backed lexical matching for that request
- **AND** matching memories that satisfy the explicit filters remain eligible for results

#### Scenario: Query-present search falls back when semantic retrieval is unavailable

- **WHEN** a client searches with non-empty query text
- **AND** semantic retrieval is temporarily unavailable
- **THEN** the system falls back to canonical PostgreSQL-backed lexical matching for that request
- **AND** the response still returns canonical memory records that satisfy the explicit filters

#### Scenario: Query-less search remains browse-style

- **WHEN** a client searches without query text
- **THEN** the system does not require semantic retrieval to produce results
- **AND** the response preserves the existing browse-style search behavior

### Requirement: Search Uses Deterministic Query-Aware Ordering

The search operation MUST return results in a deterministic order.

When a query is present and semantic retrieval returns eligible candidates, the system MUST use semantic retrieval rank as the primary ordering signal for those eligible candidates.

When multiple eligible results share the same semantic rank, the system MUST break ties by `updated_at` descending and then `id` ascending.

When a query is present and the search operation falls back to canonical PostgreSQL-backed lexical matching, the system MUST order results using the existing query-aware PostgreSQL ordering policy.

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

#### Scenario: Query fallback preserves deterministic lexical ordering

- **WHEN** a client searches with query text
- **AND** the search operation falls back to canonical PostgreSQL-backed lexical matching
- **THEN** the system orders matching memories by the existing query-aware PostgreSQL ordering policy
- **AND** the fallback result order remains deterministic

#### Scenario: Non-query searches stay chronological with deterministic ties

- **WHEN** a client searches without query text
- **THEN** the system orders matching memories by `updated_at` descending
- **AND** uses `id` ascending to break ties deterministically
