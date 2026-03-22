from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

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
            "supersedes_memory_id": request.supersedes_memory_id,
            "tags": request.tags,
            "source": request.source.model_dump(exclude_none=True),
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

    def search(
        self,
        request: MemorySearchRequest,
        ids: list[str] | None = None,
        *,
        update_access_time: bool = False,
    ) -> list[MemoryRecord]:
        memories = list(self.stored_memories.values())
        if ids is not None:
            order = {memory_id: index for index, memory_id in enumerate(ids)}
            memories = [memory for memory in memories if memory.id in order]
            memories.sort(
                key=lambda memory: (
                    order[memory.id],
                    -memory.updated_at.timestamp(),
                    memory.id,
                )
            )
        if request.namespace is not None:
            memories = [memory for memory in memories if memory.namespace == request.namespace]
        if request.scope is not None:
            memories = [memory for memory in memories if memory.scope == request.scope]
        if request.kind is not None:
            memories = [memory for memory in memories if memory.kind == request.kind]
        if request.tags:
            memories = [memory for memory in memories if all(tag in memory.tags for tag in request.tags)]
        if not request.include_archived:
            memories = [memory for memory in memories if not memory.archived]
        if request.query is not None and ids is None:
            needle = request.query.casefold()
            memories = [
                memory
                for memory in memories
                if needle in memory.title.casefold() or needle in memory.content.casefold()
            ]
            memories.sort(
                key=lambda memory: (
                    0
                    if memory.title.casefold() == needle
                    else 1
                    if needle in memory.title.casefold()
                    else 2
                    if needle in memory.content.casefold()
                    else 3,
                    -memory.confidence,
                    -memory.updated_at.timestamp(),
                    memory.id,
                )
            )
        elif ids is None:
            memories.sort(key=lambda memory: (-memory.updated_at.timestamp(), memory.id))
        if request.exclude_superseded:
            superseded_keys = {
                (memory.namespace, memory.supersedes_memory_id)
                for memory in self.stored_memories.values()
                if memory.supersedes_memory_id is not None and not memory.archived
            }
            memories = [memory for memory in memories if (memory.namespace, memory.id) not in superseded_keys]
        memories = memories[: request.limit]
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
    search_results: list[str] = field(default_factory=list)
    search_scores: dict[str, float] = field(default_factory=dict)
    search_calls: list[tuple[list[float], int]] = field(default_factory=list)

    def init(self) -> None:
        return None

    def ping(self) -> None:
        return None

    def search_memory_candidates(self, vector: list[float], *, limit: int) -> list[tuple[str, float]]:
        self.search_calls.append((vector, limit))
        limited_ids = self.search_results[:limit]
        default_scores = {memory_id: float(len(limited_ids) - index) for index, memory_id in enumerate(limited_ids)}
        return [(memory_id, self.search_scores.get(memory_id, default_scores[memory_id])) for memory_id in limited_ids]

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
    assert created.source.type == "manual"
    assert created.source.name is None


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


def test_create_memory_normalizes_source_type_before_persistence() -> None:
    request = build_create_request(source={"type": " Manual "})
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.source.type == "manual"
    assert postgres.create_calls[0][1].source.type == "manual"
    assert qdrant.upserts[0][0].source.type == "manual"


def test_create_memory_trims_source_name_and_preserves_it_when_non_blank() -> None:
    request = build_create_request(source={"type": "manual", "name": " Codex CLI "})
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.source.name == "Codex CLI"
    assert postgres.create_calls[0][1].source.name == "Codex CLI"
    assert qdrant.upserts[0][0].source.name == "Codex CLI"


def test_create_memory_omits_blank_source_name_from_canonical_shape() -> None:
    request = build_create_request(source={"type": "manual", "name": "   "})
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.source.name is None
    assert "name" not in created.source.model_dump(exclude_none=True)
    assert "name" not in postgres.create_calls[0][1].source.model_dump(exclude_none=True)
    assert "name" not in qdrant.upserts[0][0].source.model_dump(exclude_none=True)


def test_create_memory_normalizes_confidence_before_persistence() -> None:
    request = build_create_request(confidence=0.1235)
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.confidence == 0.124
    assert postgres.create_calls[0][1].confidence == 0.124
    assert qdrant.upserts[0][0].confidence == 0.124


def test_create_memory_persists_supersession_link_for_same_namespace_reference() -> None:
    prior = build_memory_record("prior-memory", build_create_request())
    request = build_create_request(supersedes_memory_id=prior.id)
    postgres = FakePostgresStore(stored_memories={prior.id: prior})
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    created = service.create_memory(request)

    assert created.supersedes_memory_id == prior.id
    assert len(postgres.create_calls) == 1
    assert postgres.create_calls[0][1].supersedes_memory_id == prior.id


def test_create_memory_rejects_missing_supersession_reference() -> None:
    request = build_create_request(supersedes_memory_id="missing-memory")
    postgres = FakePostgresStore()
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    try:
        service.create_memory(request)
    except ValueError as exc:
        assert str(exc) == "supersedes_memory_id must reference an existing memory in the same namespace"
    else:
        raise AssertionError("Expected create_memory to reject a missing supersession reference")

    assert postgres.create_calls == []
    assert qdrant.upserts == []


def test_create_memory_rejects_cross_namespace_supersession_reference() -> None:
    prior = build_memory_record("prior-memory", build_create_request(namespace="other-project"))
    request = build_create_request(supersedes_memory_id=prior.id)
    postgres = FakePostgresStore(stored_memories={prior.id: prior})
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    try:
        service.create_memory(request)
    except ValueError as exc:
        assert str(exc) == "supersedes_memory_id must reference an existing memory in the same namespace"
    else:
        raise AssertionError("Expected create_memory to reject a cross-namespace supersession reference")

    assert postgres.create_calls == []
    assert qdrant.upserts == []


def test_duplicate_write_matches_when_supersession_link_matches() -> None:
    prior = build_memory_record("prior-memory", build_create_request())
    request = build_create_request(supersedes_memory_id="prior-memory")
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(duplicate_memory=existing, stored_memories={prior.id: prior})
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    returned = service.create_memory(build_create_request(supersedes_memory_id="prior-memory"))

    assert returned.id == "existing-memory"
    assert postgres.create_calls == []
    assert qdrant.upserts == []


def test_duplicate_write_creates_new_memory_when_supersession_link_differs() -> None:
    old_prior = build_memory_record("old-prior-memory", build_create_request())
    new_prior = build_memory_record("new-prior-memory", build_create_request(title="New prior"))
    request = build_create_request(supersedes_memory_id="new-prior-memory")
    postgres = FakePostgresStore(stored_memories={old_prior.id: old_prior, new_prior.id: new_prior})
    qdrant = FakeQdrantStore()
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    returned = service.create_memory(request)

    assert returned.supersedes_memory_id == "new-prior-memory"
    assert len(postgres.create_calls) == 1
    assert qdrant.upserts[0][0].supersedes_memory_id == "new-prior-memory"


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


def test_query_present_search_advances_last_accessed_at_for_returned_memories() -> None:
    request = build_create_request(title="Existing memory", content="Helpful semantic note.")
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(stored_memories={existing.id: existing})
    qdrant = FakeQdrantStore(search_results=[existing.id])
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(query="related guidance"))

    assert len(response.results) == 1
    returned = response.results[0]
    assert returned.id == existing.id
    assert returned.last_accessed_at >= existing.last_accessed_at
    assert len(qdrant.search_calls) == 1


def test_returned_records_keep_normalized_source_shape_across_get_search_archive_and_duplicate() -> None:
    request = build_create_request(source={"type": " Manual ", "name": " Codex CLI "})
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(duplicate_memory=existing, stored_memories={existing.id: existing})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    duplicate = service.create_memory(build_create_request(source={"type": "MANUAL", "name": "Codex CLI"}))
    fetched = service.get_memory(existing.id)
    searched = service.search(MemorySearchRequest()).results[0]
    archived = service.archive_memory(existing.id)

    assert duplicate.source.model_dump(exclude_none=True) == {"type": "manual", "name": "Codex CLI"}
    assert fetched is not None
    assert fetched.source.model_dump(exclude_none=True) == {"type": "manual", "name": "Codex CLI"}
    assert searched.source.model_dump(exclude_none=True) == {"type": "manual", "name": "Codex CLI"}
    assert archived is not None
    assert archived.source.model_dump(exclude_none=True) == {"type": "manual", "name": "Codex CLI"}


def test_returned_records_keep_normalized_confidence_across_get_search_archive_and_duplicate() -> None:
    request = build_create_request(confidence=0.4567)
    existing = build_memory_record("existing-memory", request)
    postgres = FakePostgresStore(duplicate_memory=existing, stored_memories={existing.id: existing})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    duplicate = service.create_memory(build_create_request(confidence=0.9999))
    fetched = service.get_memory(existing.id)
    searched = service.search(MemorySearchRequest()).results[0]
    archived = service.archive_memory(existing.id)

    assert duplicate.confidence == 0.457
    assert fetched is not None
    assert fetched.confidence == 0.457
    assert searched.confidence == 0.457
    assert archived is not None
    assert archived.confidence == 0.457


def test_search_preserves_superseded_memories_by_default() -> None:
    prior_request = build_create_request(title="Original rule")
    prior = build_memory_record("prior-memory", prior_request)
    newer_request = build_create_request(title="Replacement rule", supersedes_memory_id=prior.id)
    newer = build_memory_record("newer-memory", newer_request)
    postgres = FakePostgresStore(stored_memories={prior.id: prior, newer.id: newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest())

    assert {memory.id for memory in response.results} == {prior.id, newer.id}


def test_search_can_exclude_superseded_memories() -> None:
    prior_request = build_create_request(title="Original rule")
    prior = build_memory_record("prior-memory", prior_request)
    newer_request = build_create_request(title="Replacement rule", supersedes_memory_id=prior.id)
    newer = build_memory_record("newer-memory", newer_request)
    postgres = FakePostgresStore(stored_memories={prior.id: prior, newer.id: newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(exclude_superseded=True))

    assert [memory.id for memory in response.results] == [newer.id]


def test_search_keeps_prior_memory_visible_when_only_archived_superseder_exists() -> None:
    prior_request = build_create_request(title="Original rule")
    prior = build_memory_record("prior-memory", prior_request)
    newer_request = build_create_request(title="Replacement rule", supersedes_memory_id=prior.id)
    archived_newer = build_memory_record("newer-memory", newer_request, archived=True)
    postgres = FakePostgresStore(stored_memories={prior.id: prior, archived_newer.id: archived_newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(exclude_superseded=True))

    assert [memory.id for memory in response.results] == [prior.id]


def test_query_present_search_can_return_semantic_match_without_direct_substring_hit() -> None:
    semantic_match = build_memory_record(
        "semantic-memory",
        build_create_request(
            title="Concise writing guidance",
            content="Prefer direct answers and avoid unnecessary filler.",
        ),
    )
    postgres = FakePostgresStore(
        stored_memories={semantic_match.id: semantic_match}
    )
    qdrant = FakeQdrantStore(search_results=[semantic_match.id])
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(query="brief replies"))

    assert [memory.id for memory in response.results] == [semantic_match.id]


def test_query_present_search_preserves_semantic_candidate_order_after_postgres_filtering() -> None:
    first = build_memory_record(
        "alpha-memory",
        build_create_request(title="Alpha", content="Semantic candidate one."),
    )
    filtered_out = build_memory_record(
        "filtered-memory",
        build_create_request(title="Filtered", tags=["other"], content="Semantic candidate two."),
    )
    second = build_memory_record(
        "beta-memory",
        build_create_request(title="Beta", content="Semantic candidate three.", tags=["style"]),
    ).model_copy(update={"updated_at": first.updated_at + timedelta(hours=1)})
    postgres = FakePostgresStore(stored_memories={first.id: first, filtered_out.id: filtered_out, second.id: second})
    qdrant = FakeQdrantStore(search_results=[filtered_out.id, first.id, second.id])
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(query="semantic", tags=["style"]))

    assert [memory.id for memory in response.results] == [first.id, second.id]


def test_query_present_search_uses_updated_at_then_id_to_break_semantic_ties() -> None:
    shared_updated_at = utcnow()
    alpha = build_memory_record(
        "alpha-memory",
        build_create_request(title="Alpha semantic", content="Shared guidance."),
    ).model_copy(update={"updated_at": shared_updated_at})
    beta = build_memory_record(
        "beta-memory",
        build_create_request(title="Beta semantic", content="Shared guidance."),
    ).model_copy(update={"updated_at": shared_updated_at})
    newer = build_memory_record(
        "newer-memory",
        build_create_request(title="Newer semantic", content="Shared guidance."),
    ).model_copy(update={"updated_at": shared_updated_at + timedelta(hours=1)})
    postgres = FakePostgresStore(stored_memories={beta.id: beta, alpha.id: alpha, newer.id: newer})
    qdrant = FakeQdrantStore(
        search_results=[beta.id, alpha.id, newer.id],
        search_scores={beta.id: 0.9, alpha.id: 0.9, newer.id: 0.9},
    )
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(query="semantic"))

    assert [memory.id for memory in response.results] == [newer.id, alpha.id, beta.id]


def test_query_present_search_returns_empty_when_qdrant_has_no_candidates() -> None:
    semantic_match = build_memory_record(
        "semantic-memory",
        build_create_request(title="Concise writing guidance", content="Prefer direct answers."),
    )
    postgres = FakePostgresStore(stored_memories={semantic_match.id: semantic_match})
    qdrant = FakeQdrantStore(search_results=[])
    service = MemoryService(postgres=postgres, qdrant=qdrant, embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest(query="semantic"))

    assert response.results == []


def test_search_without_query_uses_updated_at_then_id_ordering() -> None:
    shared_updated_at = utcnow()
    alpha = build_memory_record("alpha-memory", build_create_request(title="Alpha")).model_copy(
        update={"updated_at": shared_updated_at}
    )
    beta = build_memory_record("beta-memory", build_create_request(title="Beta")).model_copy(
        update={"updated_at": shared_updated_at}
    )
    newer = build_memory_record("newer-memory", build_create_request(title="Newer")).model_copy(
        update={"updated_at": shared_updated_at + timedelta(hours=1)}
    )
    postgres = FakePostgresStore(stored_memories={beta.id: beta, alpha.id: alpha, newer.id: newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    response = service.search(MemorySearchRequest())

    assert [memory.id for memory in response.results] == [newer.id, alpha.id, beta.id]


def test_archive_of_superseding_memory_does_not_cascade() -> None:
    prior_request = build_create_request(title="Original rule")
    prior = build_memory_record("prior-memory", prior_request)
    newer_request = build_create_request(title="Replacement rule", supersedes_memory_id=prior.id)
    newer = build_memory_record("newer-memory", newer_request)
    postgres = FakePostgresStore(stored_memories={prior.id: prior, newer.id: newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    archived = service.archive_memory(newer.id)

    assert archived is not None
    assert archived.archived is True
    assert postgres.stored_memories[prior.id].archived is False
    assert postgres.stored_memories[prior.id].supersedes_memory_id is None


def test_archive_of_superseded_memory_does_not_cascade() -> None:
    prior_request = build_create_request(title="Original rule")
    prior = build_memory_record("prior-memory", prior_request)
    newer_request = build_create_request(title="Replacement rule", supersedes_memory_id=prior.id)
    newer = build_memory_record("newer-memory", newer_request)
    postgres = FakePostgresStore(stored_memories={prior.id: prior, newer.id: newer})
    service = MemoryService(postgres=postgres, qdrant=FakeQdrantStore(), embedder=DeterministicEmbedder(8))

    archived = service.archive_memory(prior.id)

    assert archived is not None
    assert archived.archived is True
    assert postgres.stored_memories[newer.id].archived is False
    assert postgres.stored_memories[newer.id].supersedes_memory_id == prior.id


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
