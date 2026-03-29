## Why

The current integration workflow achieves deterministic starts by creating a fresh timestamped Docker Compose project for every run, but that makes repeat verification slow and expensive. Caching helps some internal steps, yet the workflow still spends most of its wall-clock time rebuilding project-specific images and recreating disposable runtime resources.

This is the right next slice because integration tests still need deterministic state, but they do not need full per-run environment churn to get it. A reusable local integration runtime with an explicit reset path can preserve correctness guarantees while making repeat runs materially cheaper.

## What Changes

- Replace the timestamped disposable integration workflow with a static, reusable local integration-test runtime.
- Add explicit lifecycle commands for setup, startup, reset, test execution, and cleanup.
- Preserve deterministic integration starts through a documented reset path instead of per-run project recreation.
- Keep the integration workflow isolated from the default local development stack and from the retrieval-eval runtime.
- Non-goal: change API behavior, retrieval behavior, or broaden the integration test scope in this slice.

## Capabilities

### New Capabilities
- `integration-test-runtime`: A reusable local runtime for integration tests with setup, reset, run, and cleanup operations.

### Modified Capabilities
- `isolated-integration-testing`: update the integration workflow requirements so deterministic starts can come from a reusable isolated runtime plus explicit reset, rather than requiring a newly created disposable stack on every run.

## Impact

- Affects integration-test scripts, Docker Compose workflow, and verification documentation.
- Adds explicit runtime lifecycle operations for integration testing.
- Reduces repeated Docker build churn and project-specific image creation during local verification.
