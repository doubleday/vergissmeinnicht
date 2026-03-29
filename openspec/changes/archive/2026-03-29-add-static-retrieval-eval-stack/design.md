## Context

The current retrieval-eval runner creates a fresh timestamped Docker Compose project, builds images, starts infrastructure, runs the eval, and tears everything down on each invocation. That keeps eval data isolated, but it makes local iteration expensive in CPU, disk, and time because the workflow keeps recreating container state that does not need to change between runs.

Retrieval evals are now the immediate product-quality loop, so the local workflow needs a cheaper steady state. The change should preserve the current live HTTP evaluation path and isolated runtime boundary while replacing per-run environment churn with a reusable stack that developers can set up once and reset deliberately.

## Goals / Non-Goals

**Goals:**
- Make manual retrieval eval runs cheap enough to repeat locally.
- Preserve isolation from the developer's normal long-lived memory stack.
- Add explicit lifecycle steps so setup, reset, run, and cleanup are inspectable.
- Avoid repeated timestamped image creation during ordinary eval use.

**Non-Goals:**
- Changing retrieval behavior, ranking policy, or fallback logic.
- Redesigning the eval dataset, metrics, or output schema.
- Adding CI orchestration or remote/shared eval infrastructure.
- Combining retrieval eval runtime with the default integration-test workflow.

## Decisions

### Use a fixed local Compose project for retrieval evals

The retrieval-eval workflow will use a stable local Compose project name and a dedicated Compose file or mode intended for eval use.

Rationale:
- A fixed project name allows Docker to reuse containers, volumes, and image tags between runs.
- This removes the largest current source of churn: timestamped project-specific resources.
- It keeps the runtime visible and inspectable through ordinary Docker commands.

Alternative considered:
- Keep the timestamped project model but add cleanup guidance. Rejected because it reduces disk accumulation only after the fact and does not improve the inner-loop runtime cost.

### Split lifecycle operations into setup, start, reset, run, and cleanup

The eval workflow should become a small set of explicit commands rather than one script that always rebuilds and destroys everything.

Rationale:
- Developers need different operations at different times: first-time setup, repeated runs, state reset, or full cleanup.
- Explicit commands make it easier to understand what the machine is doing.
- A reset command keeps data isolation without forcing image rebuilds or project recreation.

Alternative considered:
- Keep one monolithic script with internal flags. Rejected because separate commands are easier to document and easier to use correctly.

### Preserve isolated eval data through dedicated runtime state, not long-lived default-stack reuse

The static eval stack should remain separate from the developer's default `docker compose up` stack.

Rationale:
- Eval data should still be disposable and clearly separated from normal manual testing data.
- Reusing the default stack would save some work but would blur the boundary between eval state and normal development state.
- Dedicated eval volumes or collection names keep the isolation story intact.

Alternative considered:
- Run evals directly against the default local stack. Rejected because it weakens repeatability and increases contamination risk.

### Default local runs should avoid rebuilding heavy images unless dependencies change

The reusable eval workflow should prefer `up` and `run` against existing images, with setup or rebuild as explicit operations.

Rationale:
- Rebuilding image layers and unpacking large images is the dominant local cost today.
- Most retrieval-iteration runs change code or dataset contents, not dependency graphs.
- Making rebuild explicit aligns cost with intent.

Alternative considered:
- Rebuild on every run for safety. Rejected because it recreates the current pain and is unnecessary for ordinary local evaluation.

## Risks / Trade-offs

- [A static eval stack can drift if developers forget to reset state] -> Mitigation: provide an explicit reset command and document when it should be used before a fresh eval run.
- [A separate reusable stack adds another local environment to reason about] -> Mitigation: keep lifecycle commands few, named clearly, and documented next to the main eval workflow.
- [Long-lived eval images can still consume disk] -> Mitigation: add a cleanup operation that removes the reusable stack resources intentionally instead of accumulating timestamped copies.

## Migration Plan

1. Introduce the reusable retrieval-eval runtime definition and lifecycle commands.
2. Update the run script to use the static runtime by default instead of timestamped project creation.
3. Document first-time setup, reset, repeated-run usage, and cleanup.
4. Verify that manual retrieval evals still exercise the live HTTP API and save the same result artifacts.

Rollback is straightforward: the static runtime commands can be removed and the previous disposable project workflow restored if the reusable stack proves confusing or unreliable.

## Open Questions

- Should the reusable runtime live in a dedicated `docker-compose.retrieval-eval.yml` file or stay as a mode of the current integration Compose file?
- Should reset recreate volumes, clear only the eval collection, or do both depending on command?
