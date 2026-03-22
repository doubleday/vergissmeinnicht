from memory_api.services.embedding import DeterministicEmbedder


def test_embedder_is_deterministic() -> None:
    embedder = DeterministicEmbedder(dimensions=8)
    assert embedder.embed("same text") == embedder.embed("same text")
    assert len(embedder.embed("same text")) == 8
