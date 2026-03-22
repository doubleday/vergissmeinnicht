# Memory Service Proposal (Reformatted)

For this setup, keep the first version simple:

FastAPI + Qdrant + Postgres + Docker Compose, with memory exposed as a small HTTP API and optionally as an MCP server later.

This gives you:

- A self-hostable API layer via FastAPI, designed for typed Python APIs.
- A self-hosted vector store via Qdrant, with an official Docker-based local quickstart and local persistence by default (REST on localhost:6333).
- A path to standard tool integration later through MCP, an open protocol used by many agent and tool setups.

## Roadmap

### Phase 1 - Build the Smallest Useful Memory Service

Goal: make memory usable from Claude, Codex, scripts, and local models without framework lock-in.

Create one repo with four services:

- memory-api - FastAPI app
- qdrant - vector search
- postgres - structured metadata and audit trail
- embed-worker - optional background embedding pipeline if you do not want synchronous writes

At this stage, do not add Mem0 yet. Define your own API contract.

Use only four endpoints:

- POST /memories
- POST /memories/search
- GET /memories/{id}
- POST /memories/{id}/archive

This keeps the contract stable even if you later swap internals.

### Phase 2 - Define a Strict Memory Schema

Goal: avoid vector junk drawer syndrome.

Start with a table/document shape like this:

```json
{
  "id": "uuid",
  "kind": "rule | preference | example | correction | note",
  "scope": "global | project | agent | user",
  "namespace": "translation | coding | personal | etc",
  "title": "short label",
  "content": "canonical memory text",
  "tags": ["de", "formal-tone"],
  "source": {
    "type": "manual | conversation | imported | derived"
  },
  "confidence": 0.0,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "archived": false,
  "metadata": {}
}
```

Then store:

- The canonical record in Postgres.
- The embedding plus retrieval payload in Qdrant.

This split is useful because Qdrant is strong for semantic retrieval, while Postgres is better for exact metadata, lifecycle handling, and auditability.

### Phase 3 - Containerize Locally with Docker Compose

Goal: run the whole stack with one command.

Use Compose with:

- Volume for Postgres data
- Volume for Qdrant storage
- Internal network
- .env for model/provider config

Operational note: Qdrant persistence depends on storage path, and production-style deployments require care around filesystem compatibility and persistent storage.

For local development on macOS, treat this as:

- Fine for development
- Not yet your source of truth for production backups

### Phase 4 - Retrieval First, Learning Later

Goal: make memory deterministic before making it smart.

Implement retrieval in this order:

1. Exact filters (namespace, kind, tags, scope)
2. Semantic search in Qdrant
3. Optional rerank
4. Final merge in API layer

Simple search flow:

- Convert query to embedding
- Search Qdrant top-k
- Filter by namespace and scope
- Fetch canonical rows from Postgres
- Return compact memory cards

Do not auto-store random memories from chats yet. Make writes explicit:

- store_memory
- search_memory
- archive_memory

This is easier to debug across Claude, Codex, and Ollama.

### Phase 5 - Add Client Adapters

Goal: make every coding agent talk to the same memory backend.

Build thin adapters:

- Python SDK for scripts and local automation
- MCP server wrapper for Claude-compatible tool use
- OpenAI/Codex function-calling wrapper
- CLI for manual inspection

Key idea:

- One backend
- Multiple protocol adapters

Claude, Codex, and local agents all call the same store/search primitives.

### Phase 6 - Add Memory Hygiene Rules

Goal: prevent the system from becoming noisy.

Before broad adoption, add:

- Deduplication on write
- Archive instead of delete
- Confidence score
- source_type
- last_accessed_at
- Optional supersedes relation

Without this, quality degrades quickly.

Early rule:

- Only store memories that are reusable, corrective, or preference-like

### Phase 7 - Add Observability

Goal: know whether memory actually helps.

At minimum, log:

- Query text
- Retrieved IDs
- Latency
- Hit rate
- Whether retrieved memory was actually used

This matters more than fancy ranking. Otherwise, you cannot tell whether memory improves results or just adds token bloat.

### Phase 8 - Evaluate Mem0 as a Backend Option

Mem0 is worth monitoring as a universal memory layer for agents, with OSS docs showing self-hosted configurations around vector databases and model providers.

Use Mem0 in one of two ways:

- As a benchmark against your thin layer
- As a replaceable backend behind your own API

Do not let Mem0 become the public contract to clients.

## Recommended Milestone Order

### Milestone A

Local Compose stack running:

- FastAPI
- Postgres
- Qdrant

Success criteria:

- Create memory
- Search memory
- Inspect raw stored records

### Milestone B

One real client integrated:

- Claude or Codex calling search_memory and store_memory

Success criteria:

- Memory survives restarts
- Results are filtered by namespace and project

### Milestone C

Memory quality controls:

- Dedupe
- Archive
- Confidence
- Source tracking

Success criteria:

- Store remains clean after repeated usage

### Milestone D

Protocol expansion:

- MCP wrapper
- OpenAI function wrapper
- CLI

Success criteria:

- Same memory usable from multiple agents without app-specific glue

## Concrete First Cut for This Use Case

For translation and coding experiments, start with these memory kinds:

- rule
- example
- feedback
- correction
- preference

And these scopes:

- global
- project
- agent

This is enough to cover:

- Multi-agent pipelines
- Shared personal/work memory across Claude, Codex, and similar agents

## Opinionated Shortcut

Do this first:

1. Stand up Qdrant + Postgres + FastAPI in Compose.
2. Implement only explicit store/search/archive.
3. Add one MCP adapter.
4. Use it for two weeks on real work.
5. Decide whether you actually need Mem0-style auto-memory.

This sequence minimizes lock-in while still giving you a usable system quickly.

I can sketch the initial Docker Compose plus API contract next.