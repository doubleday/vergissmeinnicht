## 1. Search Contract

- [x] 1.1 Extend the search request model with optional `exclude_superseded` and keep the default backward-compatible
- [x] 1.2 Update the PostgreSQL search path to suppress memories superseded by an active memory in the same namespace only when `exclude_superseded` is enabled

## 2. Supersession-Aware Verification

- [x] 2.1 Add service and store tests covering default search behavior, opt-in superseded exclusion, and archived superseders no longer suppressing older memories
- [x] 2.2 Add tests confirming archive remains record-local for superseding and superseded memories
- [x] 2.3 Validate the change with the OpenSpec CLI and the targeted test suite, confirming no merge, restore, or traversal semantics were introduced
