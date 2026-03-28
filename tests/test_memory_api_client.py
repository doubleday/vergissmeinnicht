from __future__ import annotations

import json

import httpx
import pytest

from memory_api.client import MemoryApiClient, MemoryApiResponseError, MemoryApiTransportError
from memory_api.models import MemoryCreate, MemorySearchRequest


def build_create_request(**overrides: object) -> MemoryCreate:
    payload = {
        "kind": "rule",
        "scope": "project",
        "namespace": "test-project",
        "title": "Keep responses concise",
        "content": "Prefer direct answers.",
        "tags": ["style"],
        "source": {"type": "manual"},
        "confidence": 0.8,
        "metadata": {"author": "test"},
    }
    payload.update(overrides)
    return MemoryCreate.model_validate(payload)


def test_create_memory_posts_canonical_payload_and_parses_record() -> None:
    seen_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "id": "memory-1",
                "kind": "rule",
                "scope": "project",
                "namespace": "test-project",
                "title": "Keep responses concise",
                "content": "Prefer direct answers.",
                "tags": ["style"],
                "source": {"type": "manual"},
                "confidence": 0.8,
                "metadata": {"author": "test"},
                "created_at": "2026-03-28T10:00:00Z",
                "updated_at": "2026-03-28T10:00:00Z",
                "last_accessed_at": "2026-03-28T10:00:00Z",
                "archived": False,
            },
        )

    client = MemoryApiClient(
        base_url="http://example.test/api",
        transport=httpx.MockTransport(handler),
    )

    created = client.create_memory(build_create_request())

    assert seen_request is not None
    assert str(seen_request.url) == "http://example.test/api/memories"
    assert json.loads(seen_request.content.decode()) == {
        "kind": "rule",
        "scope": "project",
        "namespace": "test-project",
        "title": "Keep responses concise",
        "content": "Prefer direct answers.",
        "tags": ["style"],
        "source": {"type": "manual"},
        "confidence": 0.8,
        "metadata": {"author": "test"},
    }
    assert created.id == "memory-1"
    assert created.source.type == "manual"


def test_search_memories_uses_injected_transport_and_returns_typed_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "http://memory.test/memories/search"
        assert json.loads(request.content.decode()) == {
            "query": "direct answers",
            "namespace": "test-project",
            "scope": "project",
            "tags": [],
            "include_archived": False,
            "exclude_superseded": False,
            "limit": 5,
        }
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "memory-1",
                        "kind": "rule",
                        "scope": "project",
                        "namespace": "test-project",
                        "title": "Keep responses concise",
                        "content": "Prefer direct answers.",
                        "tags": ["style"],
                        "source": {"type": "manual"},
                        "confidence": 0.8,
                        "metadata": {"author": "test"},
                        "created_at": "2026-03-28T10:00:00Z",
                        "updated_at": "2026-03-28T10:00:00Z",
                        "last_accessed_at": "2026-03-28T10:00:00Z",
                        "archived": False,
                    }
                ]
            },
        )

    client = MemoryApiClient(base_url="http://memory.test", transport=httpx.MockTransport(handler))

    response = client.search_memories(
        MemorySearchRequest(query="direct answers", namespace="test-project", scope="project", limit=5)
    )

    assert len(response.results) == 1
    assert response.results[0].id == "memory-1"


def test_get_memory_raises_predictable_response_error_for_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Memory not found"})

    client = MemoryApiClient(base_url="http://memory.test", transport=httpx.MockTransport(handler))

    with pytest.raises(MemoryApiResponseError, match="memory API returned 404: Memory not found") as exc_info:
        client.get_memory("missing-memory")

    assert exc_info.value.status_code == 404


def test_create_memory_raises_predictable_response_error_for_validation_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "invalid request"})

    client = MemoryApiClient(base_url="http://memory.test", transport=httpx.MockTransport(handler))

    with pytest.raises(MemoryApiResponseError, match="memory API returned 422: invalid request") as exc_info:
        client.create_memory(build_create_request())

    assert exc_info.value.status_code == 422


def test_archive_memory_wraps_transport_failures_separately_from_api_failures() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = MemoryApiClient(base_url="http://memory.test", transport=httpx.MockTransport(handler))

    with pytest.raises(MemoryApiTransportError, match="memory API request failed: connection refused"):
        client.archive_memory("memory-1")
