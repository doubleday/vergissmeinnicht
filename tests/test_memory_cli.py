from __future__ import annotations

import json

import pytest

from memory_api import cli as memory_cli
from memory_api.client import MemoryApiResponseError, MemoryApiTransportError
from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, SearchResponse


def test_create_command_builds_typed_payload_and_prints_json(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    captured: dict[str, object] = {}
    captured_payload: list[MemoryCreate] = []

    class FakeClient:
        def __init__(self, *, base_url: str, timeout: float) -> None:
            captured["base_url"] = base_url
            captured["timeout"] = timeout

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def create_memory(self, payload: MemoryCreate) -> MemoryRecord:
            captured_payload.append(payload)
            return MemoryRecord.model_validate(
                {
                    "id": "memory-1",
                    "kind": "rule",
                    "scope": "project",
                    "namespace": "demo",
                    "title": "CLI memory",
                    "content": "Created through the CLI.",
                    "tags": ["cli", "typed"],
                    "source": {"type": "manual", "name": "operator"},
                    "confidence": 0.875,
                    "metadata": {"priority": 1},
                    "created_at": "2026-03-29T09:00:00Z",
                    "updated_at": "2026-03-29T09:00:00Z",
                    "last_accessed_at": "2026-03-29T09:00:00Z",
                    "archived": False,
                }
            )

    monkeypatch.setattr(memory_cli, "MemoryApiClient", FakeClient)

    exit_code = memory_cli.main(
        [
            "create",
            "--base-url",
            "http://memory.test",
            "--timeout",
            "3.5",
            "--kind",
            "rule",
            "--scope",
            "project",
            "--namespace",
            "demo",
            "--title",
            "CLI memory",
            "--content",
            "Created through the CLI.",
            "--tag",
            "cli",
            "--tag",
            "typed",
            "--source-type",
            "MANUAL",
            "--source-name",
            " operator ",
            "--confidence",
            "0.8752",
            "--metadata-json",
            '{"priority": 1}',
        ]
    )

    assert exit_code == 0
    assert captured["base_url"] == "http://memory.test"
    assert captured["timeout"] == 3.5
    assert len(captured_payload) == 1
    payload = captured_payload[0]
    assert payload.kind == "rule"
    assert payload.scope == "project"
    assert payload.tags == ["cli", "typed"]
    assert payload.source.type == "manual"
    assert payload.source.name == "operator"
    assert payload.confidence == 0.875
    assert payload.metadata == {"priority": 1}

    output = json.loads(capsys.readouterr().out)
    assert output["id"] == "memory-1"
    assert output["source"] == {"type": "manual", "name": "operator"}


def test_search_command_uses_shared_client_and_serializes_response(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    captured: dict[str, object] = {}
    captured_payload: list[MemorySearchRequest] = []

    class FakeClient:
        def __init__(self, *, base_url: str, timeout: float) -> None:
            captured["base_url"] = base_url
            captured["timeout"] = timeout

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def search_memories(self, payload: MemorySearchRequest) -> SearchResponse:
            captured_payload.append(payload)
            return SearchResponse.model_validate(
                {
                    "results": [
                        {
                            "id": "memory-1",
                            "kind": "rule",
                            "scope": "project",
                            "namespace": "demo",
                            "title": "CLI memory",
                            "content": "Created through the CLI.",
                            "tags": ["cli"],
                            "source": {"type": "manual"},
                            "confidence": 0.8,
                            "metadata": {},
                            "created_at": "2026-03-29T09:00:00Z",
                            "updated_at": "2026-03-29T09:00:00Z",
                            "last_accessed_at": "2026-03-29T09:00:00Z",
                            "archived": False,
                        }
                    ]
                }
            )

    monkeypatch.setattr(memory_cli, "MemoryApiClient", FakeClient)

    exit_code = memory_cli.main(
        [
            "search",
            "--query",
            "cli memory",
            "--namespace",
            "demo",
            "--scope",
            "project",
            "--tag",
            "cli",
            "--limit",
            "5",
            "--exclude-superseded",
        ]
    )

    assert exit_code == 0
    assert len(captured_payload) == 1
    payload = captured_payload[0]
    assert payload.query == "cli memory"
    assert payload.namespace == "demo"
    assert payload.scope == "project"
    assert payload.tags == ["cli"]
    assert payload.limit == 5
    assert payload.exclude_superseded is True

    output = json.loads(capsys.readouterr().out)
    assert output["results"][0]["id"] == "memory-1"


def test_get_command_reports_api_failures_with_status(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    class FakeClient:
        def __init__(self, *, base_url: str, timeout: float) -> None:
            self._response = type("Response", (), {"status_code": 404})()

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def get_memory(self, memory_id: str) -> MemoryRecord:
            raise MemoryApiResponseError(404, "memory API returned 404: Memory not found", response=self._response)

    monkeypatch.setattr(memory_cli, "MemoryApiClient", FakeClient)

    exit_code = memory_cli.main(["get", "missing-memory"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "api error [404]: memory API returned 404: Memory not found" in captured.err


def test_archive_command_reports_transport_failures_separately(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    class FakeClient:
        def __init__(self, *, base_url: str, timeout: float) -> None:
            pass

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def archive_memory(self, memory_id: str) -> MemoryRecord:
            raise MemoryApiTransportError("memory API request failed: connection refused", cause=RuntimeError("boom"))

    monkeypatch.setattr(memory_cli, "MemoryApiClient", FakeClient)

    exit_code = memory_cli.main(["archive", "memory-1"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "transport error: memory API request failed: connection refused" in captured.err


def test_create_command_reports_local_validation_failures(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("client should not be constructed for invalid input")

    monkeypatch.setattr(memory_cli, "MemoryApiClient", fail_if_called)

    exit_code = memory_cli.main(
        [
            "create",
            "--kind",
            "rule",
            "--scope",
            "project",
            "--namespace",
            "demo",
            "--title",
            "Invalid metadata",
            "--content",
            "This should fail before dispatch.",
            "--source-type",
            "manual",
            "--metadata-json",
            "[]",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "validation error: metadata-json must decode to an object" in captured.err
