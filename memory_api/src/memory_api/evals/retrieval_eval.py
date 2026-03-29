from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx


DEFAULT_BASE_URL = os.environ.get("MEMORY_API_BASE_URL", "http://127.0.0.1:8000")
DEFAULT_CORPUS_PATH = Path("evals/retrieval/starter/corpus.jsonl")
DEFAULT_QUERIES_PATH = Path("evals/retrieval/starter/queries.jsonl")
DEFAULT_TOP_K = 5
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_DATASET_NAME = "starter"
COMPARE_RUNTIME_FIELDS = (
    "embedding_provider",
    "embedding_model_name",
    "embedding_dimensions",
    "embedding_device",
    "memory_qdrant_collection",
)
COMPARE_DATASET_FIELDS = (
    ("dataset.name", ("dataset", "name")),
    ("dataset.corpus_path", ("dataset", "corpus_path")),
    ("dataset.queries_path", ("dataset", "queries_path")),
    ("top_k", ("top_k",)),
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            msg = f"invalid JSON on line {line_number} in {path}: {exc}"
            raise ValueError(msg) from exc
        if not isinstance(row, dict):
            msg = f"expected object on line {line_number} in {path}"
            raise ValueError(msg)
        rows.append(row)
    return rows


def wait_until_ready(base_url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/readyz", timeout=5.0)
            payload = response.json()
            if response.status_code == 200 and payload["status"] == "ok":
                return
        except (httpx.HTTPError, KeyError, ValueError):
            pass
        time.sleep(2)
    raise RuntimeError("memory-api did not become ready in time")


def create_memory(base_url: str, record: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(record.get("metadata", {}))
    metadata["eval_dataset_id"] = record["id"]
    response = httpx.post(
        f"{base_url}/memories",
        json={
            "kind": record["kind"],
            "scope": record["scope"],
            "namespace": record["namespace"],
            "title": record["title"],
            "content": record["content"],
            "tags": record.get("tags", []),
            "source": record.get("source", {"type": "manual"}),
            "confidence": record.get("confidence", 0.9),
            "metadata": metadata,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def search_memories(base_url: str, query: dict[str, Any], top_k: int) -> list[dict[str, Any]]:
    payload: dict[str, Any] = {
        "query": query["query"],
        "namespace": query.get("namespace"),
        "scope": query.get("scope"),
        "kind": query.get("kind"),
        "tags": query.get("tags", []),
        "include_archived": query.get("include_archived", False),
        "exclude_superseded": query.get("exclude_superseded", False),
        "limit": query.get("limit", top_k),
    }
    response = httpx.post(f"{base_url}/memories/search", json=payload, timeout=10.0)
    response.raise_for_status()
    return response.json()["results"]


def reciprocal_rank(returned_ids: list[str], relevant_ids: set[str], top_k: int) -> float:
    for index, result_id in enumerate(returned_ids[:top_k], start=1):
        if result_id in relevant_ids:
            return 1.0 / index
    return 0.0


def precision_at_k(query_results: list[dict[str, Any]], top_k: int) -> dict[str, float | int]:
    relevant_returned = sum(len(item["found_ids"]) for item in query_results)
    returned_total = sum(min(len(item["returned_ids"]), top_k) for item in query_results)
    if returned_total == 0:
        return {"value": 0.0, "numerator": 0, "denominator": 0}
    return {
        "value": relevant_returned / returned_total,
        "numerator": relevant_returned,
        "denominator": returned_total,
    }


def expected_empty_success(query_results: list[dict[str, Any]]) -> dict[str, float | int]:
    expected_empty_queries = [item for item in query_results if item["expected_empty"]]
    total = len(expected_empty_queries)
    if total == 0:
        return {"value": 0.0, "numerator": 0, "denominator": 0}
    passed = sum(1 for item in expected_empty_queries if item["expected_empty_pass"])
    return {"value": passed / total, "numerator": passed, "denominator": total}


def compute_metrics(query_results: list[dict[str, Any]], top_k: int) -> dict[str, dict[str, float | int]]:
    total = len(query_results)
    if total == 0:
        return {
            "hit@1": {"value": 0.0, "numerator": 0, "denominator": 0},
            f"recall@{top_k}": {"value": 0.0, "numerator": 0, "denominator": 0},
            f"mrr@{top_k}": {"value": 0.0, "numerator": 0.0, "denominator": 0},
            "expected-empty": {"value": 0.0, "numerator": 0, "denominator": 0},
            f"precision@{top_k}": {"value": 0.0, "numerator": 0, "denominator": 0},
        }

    hit_at_1_numerator = sum(1 for item in query_results if item["hit_at_1"])
    recall_numerator = sum(1 for item in query_results if item["missing_ids"] == [])
    mrr_numerator = sum(item["reciprocal_rank"] for item in query_results)

    return {
        "hit@1": {
            "value": hit_at_1_numerator / total,
            "numerator": hit_at_1_numerator,
            "denominator": total,
        },
        f"recall@{top_k}": {
            "value": recall_numerator / total,
            "numerator": recall_numerator,
            "denominator": total,
        },
        f"mrr@{top_k}": {
            "value": mrr_numerator / total,
            "numerator": mrr_numerator,
            "denominator": total,
        },
        "expected-empty": expected_empty_success(query_results),
        f"precision@{top_k}": precision_at_k(query_results, top_k),
    }


def summarize_results(result: dict[str, Any]) -> str:
    top_k = result["top_k"]
    metrics = result["metrics"]
    runtime = result.get("runtime", {})
    lines = [
        "Retrieval Eval Summary",
        f'- Dataset: {result["dataset"]["name"]}',
        f'- Corpus size: {result["dataset"]["corpus_size"]}',
        f'- Query count: {result["dataset"]["query_count"]}',
        f'- Embedding provider: {runtime.get("embedding_provider", "unknown")}',
        f'- Hit@1: {metrics["hit@1"]["numerator"]}/{metrics["hit@1"]["denominator"]} ({metrics["hit@1"]["value"]:.3f})',
        f'- Recall@{top_k}: {metrics[f"recall@{top_k}"]["numerator"]}/{metrics[f"recall@{top_k}"]["denominator"]} ({metrics[f"recall@{top_k}"]["value"]:.3f})',
        f'- MRR@{top_k}: {metrics[f"mrr@{top_k}"]["value"]:.3f}',
        f'- Expected-empty: {metrics["expected-empty"]["numerator"]}/{metrics["expected-empty"]["denominator"]} ({metrics["expected-empty"]["value"]:.3f})',
        f'- Precision@{top_k}: {metrics[f"precision@{top_k}"]["numerator"]}/{metrics[f"precision@{top_k}"]["denominator"]} ({metrics[f"precision@{top_k}"]["value"]:.3f})',
        "",
        "Per-query results:",
    ]
    for item in result["queries"]:
        lines.append(
            f'- {item["query_id"]}: returned={item["returned_ids"]} found={item["found_ids"]} '
            f'missing={item["missing_ids"]} unexpected={item["unexpected_ids"]} '
            f'expected_empty={item["expected_empty"]} pass={item["expected_empty_pass"]}'
        )
    return "\n".join(lines)


def _nested_get(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _relevant_rank(query_result: dict[str, Any]) -> int | None:
    relevant_ids = set(query_result.get("relevant_ids", []))
    for index, result_id in enumerate(query_result.get("returned_ids", []), start=1):
        if result_id in relevant_ids:
            return index
    return None


def compare_query_results(
    baseline_query: dict[str, Any],
    candidate_query: dict[str, Any],
) -> list[str]:
    changes: list[str] = []

    baseline_expected_empty_pass = baseline_query.get("expected_empty_pass", False)
    candidate_expected_empty_pass = candidate_query.get("expected_empty_pass", False)
    if baseline_expected_empty_pass != candidate_expected_empty_pass:
        changes.append(
            "expected-empty "
            f'{"passed" if baseline_expected_empty_pass else "failed"} -> '
            f'{"passed" if candidate_expected_empty_pass else "failed"}'
        )

    baseline_rank = _relevant_rank(baseline_query)
    candidate_rank = _relevant_rank(candidate_query)
    if baseline_rank != candidate_rank:
        if baseline_rank is None:
            changes.append(f"relevant hit entered top-k at rank {candidate_rank}")
        elif candidate_rank is None:
            changes.append(f"relevant hit dropped out of top-k from rank {baseline_rank}")
        else:
            changes.append(f"relevant hit rank {baseline_rank} -> {candidate_rank}")

    baseline_missing = baseline_query.get("missing_ids", [])
    candidate_missing = candidate_query.get("missing_ids", [])
    if baseline_missing != candidate_missing:
        changes.append(f"missing ids {baseline_missing} -> {candidate_missing}")

    baseline_unexpected = baseline_query.get("unexpected_ids", [])
    candidate_unexpected = candidate_query.get("unexpected_ids", [])
    if baseline_unexpected != candidate_unexpected:
        changes.append(
            "unexpected ids "
            f'{len(baseline_unexpected)} -> {len(candidate_unexpected)} '
            f"({baseline_unexpected} -> {candidate_unexpected})"
        )

    baseline_returned = baseline_query.get("returned_ids", [])
    candidate_returned = candidate_query.get("returned_ids", [])
    if baseline_returned != candidate_returned and baseline_rank == candidate_rank and baseline_unexpected == candidate_unexpected:
        changes.append(f"returned ids {baseline_returned} -> {candidate_returned}")

    return changes


def compare_results(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    compatibility: list[dict[str, Any]] = []
    for label, path in COMPARE_DATASET_FIELDS:
        compatibility.append(
            {
                "field": label,
                "baseline": _nested_get(baseline, path),
                "candidate": _nested_get(candidate, path),
                "matches": _nested_get(baseline, path) == _nested_get(candidate, path),
            }
        )
    for field in COMPARE_RUNTIME_FIELDS:
        compatibility.append(
            {
                "field": f"runtime.{field}",
                "baseline": baseline.get("runtime", {}).get(field),
                "candidate": candidate.get("runtime", {}).get(field),
                "matches": baseline.get("runtime", {}).get(field) == candidate.get("runtime", {}).get(field),
            }
        )

    metric_names = sorted(set(baseline.get("metrics", {})) | set(candidate.get("metrics", {})))
    metrics: list[dict[str, Any]] = []
    for name in metric_names:
        baseline_metric = baseline.get("metrics", {}).get(name, {})
        candidate_metric = candidate.get("metrics", {}).get(name, {})
        baseline_value = baseline_metric.get("value")
        candidate_value = candidate_metric.get("value")
        delta = None
        if isinstance(baseline_value, (int, float)) and isinstance(candidate_value, (int, float)):
            delta = candidate_value - baseline_value
        metrics.append(
            {
                "name": name,
                "baseline": baseline_metric,
                "candidate": candidate_metric,
                "delta": delta,
            }
        )

    baseline_queries = {item["query_id"]: item for item in baseline.get("queries", [])}
    candidate_queries = {item["query_id"]: item for item in candidate.get("queries", [])}
    changed_queries: list[dict[str, Any]] = []
    for query_id in sorted(set(baseline_queries) | set(candidate_queries)):
        baseline_query = baseline_queries.get(query_id)
        candidate_query = candidate_queries.get(query_id)
        if baseline_query is None:
            changed_queries.append(
                {"query_id": query_id, "summary": ["query added in candidate"], "baseline": None, "candidate": candidate_query}
            )
            continue
        if candidate_query is None:
            changed_queries.append(
                {"query_id": query_id, "summary": ["query missing in candidate"], "baseline": baseline_query, "candidate": None}
            )
            continue
        summary = compare_query_results(baseline_query, candidate_query)
        if summary:
            changed_queries.append(
                {
                    "query_id": query_id,
                    "query": candidate_query.get("query", baseline_query.get("query", "")),
                    "summary": summary,
                    "baseline": baseline_query,
                    "candidate": candidate_query,
                }
            )

    return {
        "baseline": {
            "dataset": baseline.get("dataset", {}).get("name"),
            "path": "",
        },
        "candidate": {
            "dataset": candidate.get("dataset", {}).get("name"),
            "path": "",
        },
        "compatibility": compatibility,
        "metrics": metrics,
        "changed_queries": changed_queries,
    }


def summarize_comparison(comparison: dict[str, Any]) -> str:
    lines = [
        "Retrieval Eval Comparison",
        f'- Baseline: {comparison["baseline"]["path"]}',
        f'- Candidate: {comparison["candidate"]["path"]}',
        "",
        "Compatibility:",
    ]
    for item in comparison["compatibility"]:
        if item["matches"]:
            lines.append(f'- {item["field"]}: match ({item["baseline"]})')
        else:
            lines.append(
                f'- {item["field"]}: differs '
                f'(baseline={item["baseline"]}, candidate={item["candidate"]})'
            )

    lines.append("")
    lines.append("Metric deltas:")
    for item in comparison["metrics"]:
        baseline_value = item["baseline"].get("value")
        candidate_value = item["candidate"].get("value")
        if isinstance(item["delta"], (int, float)):
            delta_text = f"{item['delta']:+.3f}"
        else:
            delta_text = "n/a"
        if isinstance(baseline_value, (int, float)) and isinstance(candidate_value, (int, float)):
            lines.append(
                f'- {item["name"]}: {baseline_value:.3f} -> {candidate_value:.3f} ({delta_text})'
            )
        else:
            lines.append(f'- {item["name"]}: unavailable')

    lines.append("")
    lines.append("Changed queries:")
    if not comparison["changed_queries"]:
        lines.append("- none")
    else:
        for item in comparison["changed_queries"]:
            query_label = item.get("query")
            if query_label:
                lines.append(f'- {item["query_id"]} "{query_label}": ' + "; ".join(item["summary"]))
            else:
                lines.append(f'- {item["query_id"]}: ' + "; ".join(item["summary"]))
    return "\n".join(lines)


def build_runtime_metadata() -> dict[str, str]:
    return {
        "embedding_provider": os.environ.get("EMBEDDING_PROVIDER", "unknown"),
        "embedding_model_name": os.environ.get("EMBEDDING_MODEL_NAME", ""),
        "embedding_dimensions": os.environ.get("EMBEDDING_DIMENSIONS", ""),
        "embedding_device": os.environ.get("EMBEDDING_DEVICE", ""),
        "memory_qdrant_collection": os.environ.get("MEMORY_QDRANT_COLLECTION", ""),
    }


def run_eval(
    *,
    base_url: str,
    corpus_path: Path,
    queries_path: Path,
    top_k: int,
) -> dict[str, Any]:
    wait_until_ready(base_url)
    corpus = load_jsonl(corpus_path)
    queries = load_jsonl(queries_path)

    for record in corpus:
        create_memory(base_url, record)

    query_results: list[dict[str, Any]] = []
    for query in queries:
        results = search_memories(base_url, query, top_k)
        returned_ids = [
            result.get("metadata", {}).get("eval_dataset_id", result["id"])
            for result in results[:top_k]
        ]
        relevant_ids = set(query["relevant_ids"])
        expected_empty = bool(query.get("expected_empty", False))
        found_ids = [result_id for result_id in returned_ids if result_id in relevant_ids]
        missing_ids = [result_id for result_id in query["relevant_ids"] if result_id not in returned_ids]
        unexpected_ids = [result_id for result_id in returned_ids if result_id not in relevant_ids]
        query_results.append(
            {
                "query_id": query["query_id"],
                "query": query["query"],
                "notes": query.get("notes"),
                "relevant_ids": query["relevant_ids"],
                "returned_ids": returned_ids,
                "found_ids": found_ids,
                "missing_ids": missing_ids,
                "unexpected_ids": unexpected_ids,
                "expected_empty": expected_empty,
                "expected_empty_pass": expected_empty and not returned_ids,
                "hit_at_1": bool(returned_ids) and returned_ids[0] in relevant_ids,
                "reciprocal_rank": reciprocal_rank(returned_ids, relevant_ids, top_k),
            }
        )

    return {
        "dataset": {
            "name": DEFAULT_DATASET_NAME,
            "corpus_path": str(corpus_path),
            "queries_path": str(queries_path),
            "corpus_size": len(corpus),
            "query_count": len(queries),
        },
        "base_url": base_url,
        "runtime": build_runtime_metadata(),
        "top_k": top_k,
        "metrics": compute_metrics(query_results, top_k),
        "queries": query_results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run retrieval evaluation against memory-api.")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run retrieval evaluation.")
    run_parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    run_parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    run_parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES_PATH)
    run_parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    run_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="summary",
        help="Choose JSON for machine-readable output or summary for human-readable output.",
    )

    summary_parser = subparsers.add_parser("summary", help="Render a human-readable summary from a JSON result file.")
    summary_parser.add_argument("--input", type=Path, required=True)

    compare_parser = subparsers.add_parser("compare", help="Compare two saved retrieval-eval JSON result files.")
    compare_parser.add_argument("--baseline", type=Path, required=True)
    compare_parser.add_argument("--candidate", type=Path, required=True)
    compare_parser.add_argument(
        "--output-format",
        choices=("json", "summary"),
        default="summary",
        help="Choose JSON for machine-readable output or summary for human-readable output.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "summary":
        result = json.loads(args.input.read_text(encoding="utf-8"))
        print(summarize_results(result))
        return 0

    if args.command == "compare":
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
        comparison = compare_results(baseline, candidate)
        comparison["baseline"]["path"] = str(args.baseline)
        comparison["candidate"]["path"] = str(args.candidate)
        if args.output_format == "json":
            print(json.dumps(comparison, indent=2))
        else:
            print(summarize_comparison(comparison))
        return 0

    if args.command in (None, "run"):
        result = run_eval(
            base_url=args.base_url,
            corpus_path=args.corpus,
            queries_path=args.queries,
            top_k=args.top_k,
        )
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(summarize_results(result))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"retrieval eval failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
