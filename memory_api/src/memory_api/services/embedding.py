from __future__ import annotations

import hashlib
from importlib import import_module
from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    from memory_api.config import Settings


DEFAULT_SENTENCE_TRANSFORMER_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_SENTENCE_TRANSFORMER_DEVICE = "cpu"
SENTENCE_TRANSFORMER_PROVIDER = "sentence-transformer-local"


class InvalidEmbeddingConfigError(ValueError):
    pass


class Embedder(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]: ...


class DeterministicEmbedder:
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        while len(values) < self.dimensions:
            for byte in digest:
                values.append((byte / 255.0) * 2.0 - 1.0)
                if len(values) == self.dimensions:
                    break
            digest = hashlib.sha256(digest).digest()
        return values


class SentenceTransformerEmbedder:
    def __init__(self, *, model_name: str, device: str) -> None:
        try:
            sentence_transformers = import_module("sentence_transformers")
        except ImportError as exc:
            msg = "sentence-transformers dependency is required for sentence-transformer-local embeddings"
            raise InvalidEmbeddingConfigError(msg) from exc

        try:
            self._model = sentence_transformers.SentenceTransformer(model_name, device=device)
        except Exception as exc:
            msg = f"failed to initialize local embedding model '{model_name}': {exc}"
            raise InvalidEmbeddingConfigError(msg) from exc

        dimensions = self._model.get_sentence_embedding_dimension()
        if not isinstance(dimensions, int) or dimensions <= 0:
            msg = f"local embedding model '{model_name}' did not report a valid embedding dimension"
            raise InvalidEmbeddingConfigError(msg)
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        values = _tolist(vector)
        if len(values) != self.dimensions:
            msg = (
                "local embedding model returned an unexpected vector size: "
                f"expected {self.dimensions}, got {len(values)}"
            )
            raise RuntimeError(msg)
        return values


def build_embedder(settings: Settings) -> Embedder:
    if settings.embedding_dimensions <= 0:
        msg = "embedding_dimensions must be a positive integer"
        raise InvalidEmbeddingConfigError(msg)

    if settings.embedding_provider == "deterministic-local":
        return DeterministicEmbedder(settings.embedding_dimensions)

    if settings.embedding_provider == SENTENCE_TRANSFORMER_PROVIDER:
        embedder = SentenceTransformerEmbedder(
            model_name=settings.embedding_model_name,
            device=settings.embedding_device,
        )
        if embedder.dimensions != settings.embedding_dimensions:
            msg = (
                "embedding_dimensions does not match the configured local model output: "
                f"expected {embedder.dimensions}, got {settings.embedding_dimensions}"
            )
            raise InvalidEmbeddingConfigError(msg)
        return embedder

    msg = (
        "unsupported embedding_provider "
        f"'{settings.embedding_provider}'; "
        "expected 'deterministic-local' or "
        f"'{SENTENCE_TRANSFORMER_PROVIDER}'"
    )
    raise InvalidEmbeddingConfigError(msg)


def _tolist(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        raw_values = vector.tolist()
    else:
        raw_values = list(vector)
    return [float(value) for value in raw_values]
