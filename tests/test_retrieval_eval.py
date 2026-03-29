from __future__ import annotations

import json
import os
from pathlib import Path

from memory_api.evals.retrieval_eval import build_runtime_metadata, compute_metrics, load_jsonl, summarize_results


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
