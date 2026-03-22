from __future__ import annotations

import os
import time
from uuid import uuid4

import httpx


BASE_URL = os.environ.get("MEMORY_API_BASE_URL", "http://memory-api:8000")


def wait_until_ready(timeout_seconds: int = 90) -> dict:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = httpx.get(f"{BASE_URL}/readyz", timeout=5.0)
            data = response.json()
            if response.status_code == 200 and data["status"] == "ok":
                return data
        except httpx.HTTPError:
            pass
        time.sleep(2)
    raise RuntimeError("memory-api did not become ready in time")


def create_memory(*, namespace: str, title: str, content: str, tags: list[str] | None = None) -> dict:
    response = httpx.post(
        f"{BASE_URL}/memories",
        json={
            "kind": "rule",
            "scope": "project",
            "namespace": namespace,
            "title": title,
            "content": content,
            "tags": tags or [],
            "source": {"type": "manual"},
            "confidence": 0.9,
            "metadata": {"test_run": namespace},
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def test_readyz_reports_live_dependencies() -> None:
    ready = wait_until_ready()

    assert ready["status"] == "ok"
    assert ready["checks"] == {"postgres": "ok", "qdrant": "ok"}


def test_memory_lifecycle_through_live_http_api() -> None:
    wait_until_ready()
    namespace = f"integration-{uuid4().hex[:8]}"
    created = create_memory(
        namespace=namespace,
        title="Integration lifecycle memory",
        content=f"Lifecycle verification payload {uuid4().hex}",
        tags=["integration", "lifecycle"],
    )

    fetched = httpx.get(f"{BASE_URL}/memories/{created['id']}", timeout=10.0)
    fetched.raise_for_status()
    fetched_payload = fetched.json()
    assert fetched_payload["id"] == created["id"]
    assert fetched_payload["archived"] is False

    search_before_archive = httpx.post(
        f"{BASE_URL}/memories/search",
        json={"query": created["content"], "namespace": namespace, "scope": "project"},
        timeout=10.0,
    )
    search_before_archive.raise_for_status()
    search_results_before_archive = search_before_archive.json()["results"]
    assert any(item["id"] == created["id"] for item in search_results_before_archive)

    archived = httpx.post(f"{BASE_URL}/memories/{created['id']}/archive", timeout=10.0)
    archived.raise_for_status()
    archived_payload = archived.json()
    assert archived_payload["id"] == created["id"]
    assert archived_payload["archived"] is True

    search_after_archive = httpx.post(
        f"{BASE_URL}/memories/search",
        json={"query": created["content"], "namespace": namespace, "scope": "project"},
        timeout=10.0,
    )
    search_after_archive.raise_for_status()
    assert all(item["id"] != created["id"] for item in search_after_archive.json()["results"])

    archived_search = httpx.post(
        f"{BASE_URL}/memories/search",
        json={
            "query": created["content"],
            "namespace": namespace,
            "scope": "project",
            "include_archived": True,
        },
        timeout=10.0,
    )
    archived_search.raise_for_status()
    assert any(item["id"] == created["id"] for item in archived_search.json()["results"])


def test_search_returns_exact_content_hit_from_live_stack() -> None:
    wait_until_ready()
    namespace = f"semantic-{uuid4().hex[:8]}"
    expected_content = f"Retrieval-backed integration payload {uuid4().hex}"
    created = create_memory(
        namespace=namespace,
        title="Primary retrieval memory",
        content=expected_content,
        tags=["integration", "retrieval"],
    )
    create_memory(
        namespace=namespace,
        title="Distractor retrieval memory",
        content=f"Distractor payload {uuid4().hex}",
        tags=["integration", "retrieval"],
    )

    search = httpx.post(
        f"{BASE_URL}/memories/search",
        json={"query": expected_content, "namespace": namespace, "scope": "project"},
        timeout=10.0,
    )
    search.raise_for_status()
    results = search.json()["results"]

    assert results
    assert any(item["id"] == created["id"] for item in results)
