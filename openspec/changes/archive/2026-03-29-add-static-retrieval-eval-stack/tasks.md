## 1. Reusable eval runtime

- [x] 1.1 Add a dedicated reusable retrieval-eval runtime definition with a fixed local project identity instead of timestamped per-run naming.
- [x] 1.2 Add explicit lifecycle commands for setup, startup, reset, eval execution, and cleanup.
- [x] 1.3 Ensure ordinary local eval runs reuse existing images and runtime resources unless a rebuild is explicitly requested.

## 2. Isolated reset and run flow

- [x] 2.1 Update the retrieval-eval run path so it still exercises the live HTTP API against an isolated eval runtime.
- [x] 2.2 Implement a clean reset path that prepares eval data for a fresh run without rebuilding the runtime images.
- [x] 2.3 Verify the saved retrieval-eval artifact and summary output remain compatible with the current review workflow.

## 3. Documentation and operator guidance

- [x] 3.1 Document first-time setup, repeated local runs, reset usage, and cleanup for the static retrieval-eval stack.
- [x] 3.2 Document how the reusable eval runtime stays separate from the default local stack and when developers should reset versus rebuild.
