## 1. Client Surface

- [x] 1.1 Add a typed synchronous Python client module inside the installed `memory_api` package with one method per public memory endpoint.
- [x] 1.2 Add the narrow configuration and exception surface needed for base URL selection, timeout control, injected HTTP behavior, and predictable API-failure reporting.

## 2. Verification And Documentation

- [x] 2.1 Add unit tests covering request serialization, typed response parsing, and failure handling through the client boundary without requiring a live stack.
- [x] 2.2 Add one client-level live-path verification and documentation that show the Python client as the first Milestone D adapter boundary without introducing CLI or MCP work.
