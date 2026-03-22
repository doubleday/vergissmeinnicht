# Project Overview
- `vergissmeinnicht` is a self-hosted memory backend for coding agents, scripts, and local models.
- Current scope is OpenSpec-first: the repo currently contains product and contract artifacts rather than implementation code.
- Intended stack for the first implementation is FastAPI, PostgreSQL, Qdrant, and Docker Compose.
- Product direction emphasizes a small stable HTTP API with thin adapters for MCP, Codex/OpenAI function calling, CLI, and scripts.
- The initial API boundary is create, search, get by id, and archive for memories.
- Canonical storage direction: PostgreSQL for lifecycle and exact metadata, Qdrant for retrieval payloads and embeddings.
- Early priorities are determinism, inspectability, explicit writes, and stable contract definition before infrastructure or auto-memory features.