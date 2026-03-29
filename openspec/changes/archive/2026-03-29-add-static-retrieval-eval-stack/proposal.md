## Why

The current retrieval-eval workflow recreates a disposable Docker Compose project and rebuilds eval images on each run. On local machines this is too heavy for the inner loop: it creates large timestamped images, obscures what the machine is doing, and makes retrieval iteration slower than the quality work itself.

This is the right next slice because retrieval evals are now the immediate priority, and the manual workflow needs to become cheap and predictable enough to run repeatedly before deeper search-quality changes.

## What Changes

- Replace the timestamped disposable retrieval-eval workflow with a static, reusable local eval stack.
- Add explicit commands for first-time setup, stack startup, dataset reset, eval execution, and cleanup.
- Keep retrieval evals isolated from the developer's normal local stack while avoiding per-run image churn.
- Preserve the current live HTTP eval path, starter dataset loading, and saved result output.
- Non-goal: change retrieval behavior, redesign search, add MCP work, or introduce CI orchestration in this slice.

## Capabilities

### New Capabilities
- `retrieval-eval-runtime`: A reusable local runtime workflow for retrieval evals with setup, reset, run, and cleanup operations.

### Modified Capabilities
- `retrieval-evaluation`: update the manual eval workflow requirements so local runs can use a reusable isolated runtime instead of a newly created disposable stack each time.

## Impact

- Affects retrieval-eval scripts, Docker Compose workflow, and local eval documentation.
- Adds explicit lifecycle operations for the eval runtime.
- Reduces Docker build churn, disk growth, and repeated startup overhead during retrieval iteration.
