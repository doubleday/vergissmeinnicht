from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from memory_api.models import MemoryRecord


class QdrantStore:
    def __init__(self, url: str, collection: str, vector_size: int) -> None:
        self.collection = collection
        self.client = QdrantClient(url=url)
        self.vector_size = vector_size

    def init(self) -> None:
        if self.client.collection_exists(self.collection):
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=rest.VectorParams(size=self.vector_size, distance=rest.Distance.COSINE),
        )

    def ping(self) -> None:
        self.client.get_collections()

    def upsert_memory(self, memory: MemoryRecord, vector: list[float]) -> None:
        self.client.upsert(
            collection_name=self.collection,
            points=[
                rest.PointStruct(
                    id=memory.id,
                    vector=vector,
                    payload={
                        "kind": memory.kind,
                        "scope": memory.scope,
                        "namespace": memory.namespace,
                        "title": memory.title,
                        "content": memory.content,
                        "tags": memory.tags,
                        "archived": memory.archived,
                    },
                )
            ],
        )
