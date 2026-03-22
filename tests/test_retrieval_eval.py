from __future__ import annotations

import json
from pathlib import Path

from memory_api.evals.retrieval_eval import compute_metrics, load_jsonl, summarize_results


def test_load_jsonl_reads_objects_in_order(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text('{"id":"a"}\n{"id":"b"}\n', encoding="utf-8")

    rows = load_jsonl(path)

    assert rows == [{"id": "a"}, {"id": "b"}]


def test_compute_metrics_uses_hit_recall_and_mrr() -> None:
    query_results = [
        {
            "hit_at_1": True,
            "missing_ids": [],
            "reciprocal_rank": 1.0,
        },
        {
            "hit_at_1": False,
            "missing_ids": ["m2"],
            "reciprocal_rank": 0.5,
        },
    ]

    metrics = compute_metrics(query_results, top_k=5)

    assert metrics["hit@1"] == {"value": 0.5, "numerator": 1, "denominator": 2}
    assert metrics["recall@5"] == {"value": 0.5, "numerator": 1, "denominator": 2}
    assert metrics["mrr@5"] == {"value": 0.75, "numerator": 1.5, "denominator": 2}


def test_summarize_results_reports_metrics_and_query_details(tmp_path: Path) -> None:
    result = {
        "dataset": {
            "name": "starter",
            "corpus_size": 2,
            "query_count": 1,
        },
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 1.0, "numerator": 1, "denominator": 1},
            "recall@5": {"value": 1.0, "numerator": 1, "denominator": 1},
            "mrr@5": {"value": 1.0, "numerator": 1.0, "denominator": 1},
        },
        "queries": [
            {
                "query_id": "q1",
                "returned_ids": ["m1"],
                "found_ids": ["m1"],
                "missing_ids": [],
            }
        ],
    }

    summary = summarize_results(result)

    assert "Retrieval Eval Summary" in summary
    assert "Hit@1: 1/1 (1.000)" in summary
    assert "q1: returned=['m1'] found=['m1'] missing=[]" in summary


def test_summary_command_shape_round_trips_json(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    payload = {
        "dataset": {"name": "starter", "corpus_size": 1, "query_count": 1},
        "top_k": 5,
        "metrics": {
            "hit@1": {"value": 1.0, "numerator": 1, "denominator": 1},
            "recall@5": {"value": 1.0, "numerator": 1, "denominator": 1},
            "mrr@5": {"value": 1.0, "numerator": 1.0, "denominator": 1},
        },
        "queries": [{"query_id": "q1", "returned_ids": ["m1"], "found_ids": ["m1"], "missing_ids": []}],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert summarize_results(loaded).startswith("Retrieval Eval Summary")
