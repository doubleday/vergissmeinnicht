from __future__ import annotations

from dataclasses import dataclass, field

from memory_api.models import MemoryCreate, MemoryRecord, MemorySearchRequest, utcnow
from memory_api.services.embedding import DeterministicEmbedder
from memory_api.services.memory_service import MemoryService
from memory_api.services.postgres import normalize_duplicate_text


def build_create_request(**overrides: object) -> MemoryCreate:
    payload = {
        "kind": "rule",
        "scope": "project",
        "namespace": "test-project",
        "title": " Keep responses concise ",
        "content": " Prefer direct answers with examples only when needed. ",
        "tags": ["style"],
        "source": {"type": "manual"},
        "confidence": 0.8,
        "metadata": {"author": "test"},
    }
    payload.update(overrides)
    return MemoryCreate.model_validate(payload)


def build_memory_record(memory_id: str, request: MemoryCreate, *, archived: bool = False) -> MemoryRecord:
    now = utcnow()
    return MemoryRecord.model_validate(
        {
            "id": memory_id,
            "kind": request.kind,
            "scope": request.scope,
            "namespace": request.namespace,
            "title": request.title,
            "content": request.content,
            "tags": request.tags,
            "source": request.source.model_dump(),
            "confidence": request.confidence,
            "metadata": request.metadata,
            "created_at": now,
            "updated_at": now,
            "last_accessed_at": now,
            "archived": archived,
        }
    )


@dataclass
class FakePostgresStore:
    duplicate_memory: MemoryRecord | None = None
    created_memory: MemoryRecord | None = None
    duplicate_requests: list[MemoryCreate] = field(default_factory=list)
    create_calls: list[tuple[str, MemoryCreate]] = field(default_factory=list)
    stored_memories: dict[str, MemoryRecord] = field(default_factory=dict)

    def init(self) -> None:
        return None

    def ping(self) -> None:
        return None

    def find_active_duplicate_memory(self, request: MemoryCreate) -> MemoryRecord | None:
        self.duplicate_requests.append(request)
        return self.duplicate_memory

    def create_memory(self, memory_id: str, request: MemoryCreate) -> MemoryRecord:
        self.create_calls.append((memory_id, request))
        memory = self.created_memory or build_memory_record(memory_id, request)
        self.stored_memories[memory.id] = memory
        return memory

    def get_memory(self, memory_id: str, *, update_access_time: bool = False) -> MemoryRecord | None:
        memory = self.stored_memories.get(memory_id)
        if memory is None:
            return None
        if not update_access_time:
            return memory
        accessed_memory = memory.model_copy(update={"last_accessed_at": utcnow()})
        self.stored_memories[memory_id] = accessed_memory
        return accessed_memory

    def archive_memory(self, memory_id: str) -> MemoryRecord | None:
        memory = self.stored_memories.get(memory_id)
        if memory is None:
            return None
        archived_memory = memory.model_copy(update={"archived": True, "updated_at": utcnow()})
        self.stored_memories[memory_id] = archived_memory
        return archived_memory

    def search(self, request: object, *, update_access_time: bool = False) -> list[MemoryRecord]:
        memories = list(self.stored_memories.values())
        if not update_access_time:
            return memories
        accessed_at = utcnow()
        updated_memories: list[MemoryRecord] = []
        for memory in memories:
            accessed_memory = memory.model_copy(update={"last_accessed_at": accessed_at})
            self.stored_memories[memory.id] = accessed_memory
            updated_memories.append(accessed_memory)
        return updated_memories


@dataclass
class FakeQdrantStore:
    upserts: list[tuple[MemoryRecord, list[float]]] = field(default_factory=list)

    def init(self) -> None:
        return None

    def ping(self) -> None:
        return None

    def upsert_memory(self, memory: MemoryRecord, vector: list[float]) -> None:
        self.upserts.append((memory, vector))


def test_create_memory_inserts_new_record_when_no_active_duplicate_exists() -> None:
    request = build_create_request()
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.id == postgres.create_calls[0][0]
    assert len(postgres.duplicate_requests) == 1
    assert len(postgres.create_calls) == 1
    assert len(qdrant.upserts) == 1
    assert qdrant.upserts[0][0].id == created.id
    assert created.last_accessed_at == created.created_at


def test_create_memory_returns_existing_record_for_duplicate_active_write() -> None:
    request = build_create_request(title="Keep responses concise", content="Prefer direct answers.")
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(duplicate_memory=existing)
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    returned = service.create_memory(build_create_request(title="  Keep responses concise  ", content="  Prefer direct answers.  "))

    assert returned.id == "existing-memory"
    assert postgres.create_calls == []
    assert qdrant.upserts == []
    assert returned.last_accessed_at == existing.last_accessed_at


def test_archived_match_does_not_block_new_write() -> None:
    request = build_create_request()
    archived_match = build_memory_record("archived-memory", request, archived=True)
    postgres = FakePostgresStore(created_memory=build_memory_record("new-memory", request))
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    returned = service.create_memory(request)

    assert archived_match.archived is True
    assert returned.id == "new-memory"
    assert len(postgres.create_calls) == 1
    assert len(qdrant.upserts) == 1


def test_get_memory_advances_last_accessed_at_for_existing_memory() -> None:
    request = build_create_request()
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(stored_memories={existing.id: existing})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    returned = service.get_memory(existing.id)

    assert returned is not None
    assert returned.id == existing.id
    assert returned.last_accessed_at >= existing.last_accessed_at
    assert returned.updated_at == existing.updated_at


def test_search_advances_last_accessed_at_for_returned_memories() -> None:
    request = build_create_request()
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(stored_memories={existing.id: existing})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest())

    assert len(response.results) == 1
    returned = response.results[0]
    assert returned.id == existing.id
    assert returned.last_accessed_at >= existing.last_accessed_at
    assert returned.updated_at == existing.updated_at


def test_archive_preserves_last_accessed_at() -> None:
    request = build_create_request()
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(stored_memories={existing.id: existing})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    archived = service.archive_memory(existing.id)

    assert archived is not None
    assert archived.archived is True
    assert archived.last_accessed_at == existing.last_accessed_at


def test_normalize_duplicate_text_trims_whitespace() -> None:
    assert normalize_duplicate_text("  keep this  ") == "keep this"
