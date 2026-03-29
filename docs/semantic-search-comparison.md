# Semantic Search Comparison

## Purpose

This document explains the high-level idea behind comparing retrieval-eval runs.

The goal is not to redesign search. The goal is to make retrieval behavior easier to review before changing retrieval logic further.

## The Core Problem

Semantic search changes are hard to judge from intuition alone.

A retrieval change can:

- improve one query while hurting another
- keep the same aggregate score while changing which memories are returned
- appear better only because the runtime, model, or collection changed
- introduce more false positives even when the top result still looks correct

Without a comparison workflow, teams end up reading raw JSON artifacts or relying on anecdotal CLI checks.

## What We Mean By Comparison

A comparison looks at two saved retrieval-eval artifacts:

- a baseline run
- a candidate run

It asks:

- Did the metrics move?
- Which queries changed?
- Did relevant results move up or down?
- Did expected-empty queries start returning memories?
- Are we comparing the same dataset and a compatible runtime setup?

This keeps evaluation focused on observable retrieval behavior rather than assumptions about why the system changed.

## Why This Matters

Comparing runs creates a review loop that is:

- repeatable
- reviewable in code review
- lightweight enough for local iteration
- safe against accidental apples-to-oranges comparisons

That matters when experimenting with:

- embedding runtime changes
- model changes
- Qdrant collection changes
- search-setting changes
- later retrieval-quality improvements

## What Good Comparison Output Should Show

At a high level, a useful comparison should surface three things.

### 1. Compatibility

The comparison should make it obvious whether the two runs used:

- the same dataset
- the same top-k setting
- the same embedding provider
- the same model and vector dimensions
- the same or intentionally different collection setup

This is the guardrail against misleading conclusions.

### 2. Metric Deltas

The comparison should show how the existing retrieval metrics changed between runs.

Examples:

- `hit@1`
- `recall@5`
- `mrr@5`
- `expected-empty`
- `precision@5`

These metrics help answer whether the candidate run looks broadly better, worse, or unchanged.

### 3. Query-Level Changes

Aggregate metrics are not enough on their own.

A comparison should also show which queries changed in review-relevant ways, such as:

- a relevant result moved lower
- a relevant result dropped out of the top-k
- an expected-empty query stopped passing
- unexpected results increased or decreased

This is where most retrieval regressions become understandable.

## What This Does Not Mean

Run comparison does not automatically mean strong semantic-quality evidence.

Comparison infrastructure helps answer:

- what changed
- where it changed
- whether the comparison is fair

It does not by itself answer:

- whether the dataset is representative enough
- whether deterministic-local results reflect real semantic quality
- whether one provider is universally better

Those questions depend on dataset quality and runtime choice.

## How To Interpret It

The comparison workflow is most useful in two modes.

### Deterministic-Local Runs

Use these for:

- regression checks
- workflow validation
- stable local iteration

These runs are useful for comparing behavior over time, but they are not strong evidence of real-world semantic quality.

### Real-Provider Runs

Use these for:

- higher-signal retrieval review
- embedding-runtime comparisons
- pre-change or post-change quality checks

These runs are more meaningful for semantic quality, but only when the saved provenance makes the comparison intentional and clear.

## Practical Outcome

Meaningful progress in retrieval evaluation looks like this:

1. Save retrieval-eval artifacts consistently.
2. Compare baseline and candidate artifacts directly.
3. Review metric deltas and changed queries together.
4. Use those findings to decide whether a retrieval-related change is worth keeping.

That gives the project a disciplined retrieval-quality loop without prematurely expanding into broad automation or search redesign.
