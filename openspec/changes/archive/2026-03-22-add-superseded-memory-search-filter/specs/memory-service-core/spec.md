## ADDED Requirements

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
