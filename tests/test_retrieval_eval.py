from __future__ import annotations

import json
from pathlib import Path

from memory_api.evals.retrieval_eval import (
    build_runtime_metadata,
    compare_results,
    compute_metrics,
    load_jsonl,
    summarize_comparison,
    summarize_results,
)


def test_load_jsonl_reads_objects_in_order(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text('{"id":"a"}\n{"id":"b"}\n', encoding="utf-8")

    rows = load_jsonl(path)

    assert rows == [{"id": "a"}, {"id": "b"}]


def test_compute_metrics_includes_false_positive_aware_metrics() -> None:
    query_results = [
        {
            "hit_at_1": True,
            "missing_ids": [],
            "reciprocal_rank": 1.0,
            "found_ids": ["m1"],
            "returned_ids": ["m1", "m2"],
            "expected_empty": False,
            "expected_empty_pass": False,
        },
        {
            "hit_at_1": False,
            "missing_ids": ["m2"],
            "reciprocal_rank": 0.5,
            "found_ids": [],
            "returned_ids": ["m4"],
            "expected_empty": True,
            "expected_empty_pass": False,
        },
    ]

    metrics = compute_metrics(query_results, top_k=5)

    assert metrics["hit@1"] == {"value": 0.5, "numerator": 1, "denominator": 2}
    assert metrics["recall@5"] == {"value": 0.5, "numerator": 1, "denominator": 2}
    assert metrics["mrr@5"] == {"value": 0.75, "numerator": 1.5, "denominator": 2}
    assert metrics["expected-empty"] == {"value": 0.0, "numerator": 0, "denominator": 1}
    assert metrics["precision@5"] == {"value": 1 / 3, "numerator": 1, "denominator": 3}


def test_summarize_results_reports_metrics_and_query_details(tmp_path: Path) -> None:
    result = {
        "dataset": {
            "name": "starter",
            "corpus_size": 2,
            "query_count": 1,
        },
        "runtime": {
            "embedding_provider": "deterministic-local",
        },
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 1.0, "numerator": 1, "denominator": 1},
            "recall@5": {"value": 1.0, "numerator": 1, "denominator": 1},
            "mrr@5": {"value": 1.0, "numerator": 1.0, "denominator": 1},
            "expected-empty": {"value": 1.0, "numerator": 1, "denominator": 1},
            "precision@5": {"value": 0.5, "numerator": 1, "denominator": 2},
        },
        "queries": [
            {
                "query_id": "q1",
                "returned_ids": ["m1"],
                "found_ids": ["m1"],
                "missing_ids": [],
                "unexpected_ids": [],
                "expected_empty": False,
                "expected_empty_pass": False,
            }
        ],
    }

    summary = summarize_results(result)

    assert "Retrieval Eval Summary" in summary
    assert "Embedding provider: deterministic-local" in summary
    assert "Hit@1: 1/1 (1.000)" in summary
    assert "Expected-empty: 1/1 (1.000)" in summary
    assert "Precision@5: 1/2 (0.500)" in summary
    assert "q1: returned=['m1'] found=['m1'] missing=[] unexpected=[] expected_empty=False pass=False" in summary


def test_summary_command_shape_round_trips_json(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    payload = {
        "dataset": {"name": "starter", "corpus_size": 1, "query_count": 1},
        "runtime": {"embedding_provider": "deterministic-local"},
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 1.0, "numerator": 1, "denominator": 1},
            "recall@5": {"value": 1.0, "numerator": 1, "denominator": 1},
            "mrr@5": {"value": 1.0, "numerator": 1.0, "denominator": 1},
            "expected-empty": {"value": 0.0, "numerator": 0, "denominator": 0},
            "precision@5": {"value": 1.0, "numerator": 1, "denominator": 1},
        },
        "queries": [
            {
                "query_id": "q1",
                "returned_ids": ["m1"],
                "found_ids": ["m1"],
                "missing_ids": [],
                "unexpected_ids": [],
                "expected_empty": False,
                "expected_empty_pass": False,
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert summarize_results(loaded).startswith("Retrieval Eval Summary")


def test_build_runtime_metadata_reads_embedding_environment(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence-transformer-local")
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "384")
    monkeypatch.setenv("EMBEDDING_DEVICE", "cpu")
    monkeypatch.setenv("MEMORY_QDRANT_COLLECTION", "memories_eval")

    metadata = build_runtime_metadata()

    assert metadata == {
        "embedding_provider": "sentence-transformer-local",
        "embedding_model_name": "BAAI/bge-small-en-v1.5",
        "embedding_dimensions": "384",
        "embedding_device": "cpu",
        "memory_qdrant_collection": "memories_eval",
    }


def test_compare_results_reports_metric_query_and_compatibility_deltas() -> None:
    baseline = {
        "dataset": {
            "name": "starter",
            "corpus_path": "evals/retrieval/starter/corpus.jsonl",
            "queries_path": "evals/retrieval/starter/queries.jsonl",
        },
        "runtime": {
            "embedding_provider": "deterministic-local",
            "embedding_model_name": "bge",
            "embedding_dimensions": "32",
            "embedding_device": "cpu",
            "memory_qdrant_collection": "memories_eval_a",
        },
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 0.5},
            "expected-empty": {"value": 0.0},
        },
        "queries": [
            {
                "query_id": "q1",
                "query": "brief replies",
                "relevant_ids": ["m1"],
                "returned_ids": ["m1", "m2"],
                "missing_ids": [],
                "unexpected_ids": ["m2"],
                "expected_empty": False,
                "expected_empty_pass": False,
            },
            {
                "query_id": "q2",
                "query": "weather tomorrow",
                "relevant_ids": [],
                "returned_ids": ["m3"],
                "missing_ids": [],
                "unexpected_ids": ["m3"],
                "expected_empty": True,
                "expected_empty_pass": False,
            },
        ],
    }
    candidate = {
        "dataset": {
            "name": "starter",
            "corpus_path": "evals/retrieval/starter/corpus.jsonl",
            "queries_path": "evals/retrieval/starter/queries.jsonl",
        },
        "runtime": {
            "embedding_provider": "deterministic-local",
            "embedding_model_name": "bge",
            "embedding_dimensions": "32",
            "embedding_device": "cpu",
            "memory_qdrant_collection": "memories_eval_b",
        },
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 1.0},
            "expected-empty": {"value": 1.0},
        },
        "queries": [
            {
                "query_id": "q1",
                "query": "brief replies",
                "relevant_ids": ["m1"],
                "returned_ids": ["m2", "m1"],
                "missing_ids": [],
                "unexpected_ids": ["m2"],
                "expected_empty": False,
                "expected_empty_pass": False,
            },
            {
                "query_id": "q2",
                "query": "weather tomorrow",
                "relevant_ids": [],
                "returned_ids": [],
                "missing_ids": [],
                "unexpected_ids": [],
                "expected_empty": True,
                "expected_empty_pass": True,
            },
        ],
    }

    comparison = compare_results(baseline, candidate)

    assert any(
        item["field"] == "runtime.memory_qdrant_collection" and item["matches"] is False
        for item in comparison["compatibility"]
    )
    assert any(
        item["name"] == "hit@1" and item["delta"] == 0.5
        for item in comparison["metrics"]
    )
    assert comparison["changed_queries"][0]["query_id"] == "q1"
    assert "relevant hit rank 1 -> 2" in comparison["changed_queries"][0]["summary"]
    assert any(
        item["query_id"] == "q2" and "expected-empty failed -> passed" in item["summary"]
        for item in comparison["changed_queries"]
    )


def test_summarize_comparison_renders_changed_queries_only() -> None:
    comparison = {
        "baseline": {"path": "baseline.json"},
        "candidate": {"path": "candidate.json"},
        "compatibility": [
            {"field": "dataset.name", "baseline": "starter", "candidate": "starter", "matches": True},
            {
                "field": "runtime.memory_qdrant_collection",
                "baseline": "a",
                "candidate": "b",
                "matches": False,
            },
        ],
        "metrics": [
            {
                "name": "hit@1",
                "baseline": {"value": 0.75},
                "candidate": {"value": 0.5},
                "delta": -0.25,
            }
        ],
        "changed_queries": [
            {
                "query_id": "q7",
                "query": "weather tomorrow",
                "summary": ["expected-empty failed -> passed", "unexpected ids 5 -> 0 ([] -> [])"],
            }
        ],
    }

    summary = summarize_comparison(comparison)

    assert "Retrieval Eval Comparison" in summary
    assert "dataset.name: match (starter)" in summary
    assert "runtime.memory_qdrant_collection: differs (baseline=a, candidate=b)" in summary
    assert "hit@1: 0.750 -> 0.500 (-0.250)" in summary
    assert 'q7 "weather tomorrow": expected-empty failed -> passed' in summary
