from __future__ import annotations

from types import SimpleNamespace

import pytest

from memory_api.config import Settings
from memory_api.services.embedding import (
    SENTENCE_TRANSFORMER_PROVIDER,
    DeterministicEmbedder,
    InvalidEmbeddingConfigError,
    SentenceTransformerEmbedder,
    build_embedder,
)


def test_embedder_is_deterministic() -> None:
    embedder = DeterministicEmbedder(dimensions=8)
    assert embedder.embed("same text") == embedder.embed("same text")
    assert len(embedder.embed("same text")) == 8


def test_build_embedder_uses_deterministic_provider_settings() -> None:
    settings = Settings(
        embedding_provider="deterministic-local",
        embedding_dimensions=16,
    )

    embedder = build_embedder(settings)

    assert isinstance(embedder, DeterministicEmbedder)
    assert embedder.dimensions == 16


def test_build_embedder_rejects_unsupported_provider() -> None:
    settings = Settings(
        embedding_provider="unknown-provider",
        embedding_dimensions=8,
    )

    with pytest.raises(InvalidEmbeddingConfigError, match="unsupported embedding_provider"):
        build_embedder(settings)


def test_build_embedder_initializes_sentence_transformer_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    created_models: list[tuple[str, str]] = []

    class FakeSentenceTransformer:
        def __init__(self, model_name: str, *, device: str) -> None:
            created_models.append((model_name, device))

        def get_sentence_embedding_dimension(self) -> int:
            return 4

        def encode(self, _text: str, **_kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(tolist=lambda: [0.1, -0.2, 0.3, -0.4])

    monkeypatch.setattr(
        "memory_api.services.embedding.import_module",
        lambda name: SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )
    settings = Settings(
        embedding_provider=SENTENCE_TRANSFORMER_PROVIDER,
        embedding_dimensions=4,
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
    )

    embedder = build_embedder(settings)

    assert isinstance(embedder, SentenceTransformerEmbedder)
    assert created_models == [("BAAI/bge-small-en-v1.5", "cpu")]
    assert embedder.embed("semantic text") == [0.1, -0.2, 0.3, -0.4]


def test_build_embedder_rejects_dimension_mismatch_for_sentence_transformer_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSentenceTransformer:
        def __init__(self, model_name: str, *, device: str) -> None:
            self.model_name = model_name
            self.device = device

        def get_sentence_embedding_dimension(self) -> int:
            return 384

        def encode(self, _text: str, **_kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(tolist=lambda: [0.0] * 384)

    monkeypatch.setattr(
        "memory_api.services.embedding.import_module",
        lambda name: SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )
    settings = Settings(
        embedding_provider=SENTENCE_TRANSFORMER_PROVIDER,
        embedding_dimensions=32,
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
    )

    with pytest.raises(InvalidEmbeddingConfigError, match="embedding_dimensions does not match"):
        build_embedder(settings)


def test_build_embedder_surfaces_local_model_initialization_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSentenceTransformer:
        def __init__(self, model_name: str, *, device: str) -> None:
            raise RuntimeError(f"cannot load {model_name} on {device}")

    monkeypatch.setattr(
        "memory_api.services.embedding.import_module",
        lambda name: SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )
    settings = Settings(
        embedding_provider=SENTENCE_TRANSFORMER_PROVIDER,
        embedding_dimensions=384,
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
    )

    with pytest.raises(InvalidEmbeddingConfigError, match="failed to initialize local embedding model"):
        build_embedder(settings)
