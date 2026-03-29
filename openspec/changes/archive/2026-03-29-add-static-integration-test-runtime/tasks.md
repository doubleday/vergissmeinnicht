## 1. Reusable integration runtime

- [x] 1.1 Add a dedicated reusable integration-test runtime definition with a fixed local project identity and fixed image names.
- [x] 1.2 Add explicit lifecycle commands for integration setup, startup, reset, test execution, and cleanup.
- [x] 1.3 Ensure ordinary local integration runs reuse existing runtime resources unless a rebuild is explicitly requested.

## 2. Deterministic reset flow

- [x] 2.1 Implement a reset path that restores clean PostgreSQL and Qdrant integration state before tests run.
- [x] 2.2 Update the integration run path so it still exercises the live HTTP API and smoke verification flow against the isolated runtime.
- [x] 2.3 Verify that repeated integration runs start from deterministic state and remain isolated from the default local stack.

## 3. Documentation and operator guidance

- [x] 3.1 Document first-time setup, repeated local runs, reset usage, and cleanup for the static integration-test runtime.
- [x] 3.2 Document how deterministic reset differs from rebuild and how the integration runtime stays separate from default local and retrieval-eval workflows.
