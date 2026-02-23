# Summarizer ↔ RSSReader Alignment TODO

Owner: Codex
Scope: Integrate LangGraph/LangChain-style orchestration into RSSReader research-agent and implement the high-impact reuse plan from `summarizer_rssreader.md`.

## Guiding Principles
- Keep RSSReader citation format unchanged: `- [Title](url) (ID: <id>)`.
- Prefer additive changes with feature flags for safe rollout.
- Use Universal Tools for web search when available.

## Plan (Step-by-step)
1) [x] LangGraph integration
   - Add LangGraph orchestrator (planner → retrieval → web search → synthesis → verification).
   - Feature flag via config; fallback to native orchestrator.

2) [x] Retrieval fusion upgrades
   - Add RRF fusion option and configurable fusion strategy.
   - Add optional two-phase embedding rerank (small candidate set).

3) [x] Web search augmentation
   - Use Universal Tools DDG search when available; fallback to Google CSE or lite scraping.
   - Wire into LangGraph flow and optionally native orchestrator.

4) [ ] Quality + safety layer
   - Add verification step for citation compliance and basic answer quality signals.
   - Emit simple quality metadata in responses (non-breaking).

5) [ ] Caching and performance
   - Add semantic cache (Redis-backed) for repeated queries.
   - Add hash-based incremental embedding checks for ingestion.

6) [ ] Observability
   - Add Prometheus metrics (latency, cache hit rate, citation compliance).

7) [x] Tests
   - Add unit tests for RRF fusion and LangGraph flow.
   - Add Playwright UI smoke test and backend health check.

## Changelog
- 2026-01-18: Created alignment plan and changelog scaffold.
- 2026-01-18: Added LangGraph orchestrator with planner/retrieval/web/synthesis/verification flow.
- 2026-01-18: Added RRF fusion and optional embedding rerank; wired config flags.
- 2026-01-18: Added Universal Tools-backed web search with DDG fallback; wired into topic updates and LangGraph.
- 2026-01-18: Added RRF fusion unit test.
- 2026-01-18: Installed LangGraph and set it as the default orchestrator.
- 2026-01-18: Added Playwright UI smoke test and backend health check test.
- 2026-01-18: Added drift dashboard (A2UI) with in-memory drift metrics.
- 2026-01-18: Arize Phoenix not available on Python 3.14 in current venv; dashboard uses local drift metrics.
- 2026-01-18: Added query expansion agent (functiongemma), expansion logging, and wired expansion into LangGraph + native orchestrators with optional web search.
- 2026-01-18: Added OTel span export toggle and spans for embedding/vector/fulltext search to close telemetry gaps.
