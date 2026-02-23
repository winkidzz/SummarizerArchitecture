# SummarizerArchitecture ↔ RSSReader Research-Agent Alignment

## Scope
This document compares the SummarizerArchitecture monorepo with the RSSReader Research-Agent (macchat/projects/rssreader/research-agent), highlighting reusable capabilities, synergies, differences, and integration patterns.

## What SummarizerArchitecture Provides (Quick Map)
- Pattern library (116 markdown docs) covering RAG + AI design patterns, healthcare use cases, vendor guides.
- Three query apps:
  - pattern-query-app: ADK + ChromaDB query tool for patterns.
  - semantic-pattern-query-app: production-grade 7-layer RAG with hybrid retrieval, telemetry, caching.
  - agentic-pattern-query-app: multi-agent orchestration with supervisor + specialists.

## Capabilities Reusable in RSSReader
- Hybrid retrieval and reranking:
  - Two-phase embeddings and RRF fusion from semantic-pattern-query-app for better recall/precision.
  - BM25 + vector fusion patterns can map to Postgres FTS + Qdrant in RSSReader.
- Quality metrics pipeline:
  - Real-time faithfulness/relevancy/hallucination scoring with structured metrics output.
- Web knowledge base + web search augmentation:
  - Trafilatura/DuckDuckGo hybrid pipeline for external context when RSS is thin.
- Semantic caching:
  - Redis-based cache for similar queries to reduce latency and costs.
- Observability stack:
  - Prometheus + Grafana dashboards and structured telemetry.
- Multi-agent roles:
  - Supervisor + Retrieval + Synthesis + Verification agents as a stronger alternative to planner-only orchestration.
- Evaluation harness:
  - Benchmarking and evaluation scripts, test suites for retrieval and generation quality.

## Synergies With Current RSSReader Architecture
- Both are FastAPI-based services with LLM-driven RAG and tool use.
- Both can leverage Ollama for local inference and embeddings.
- Both already use vector search (Qdrant in RSSReader, Qdrant/Chroma in Summarizer).
- Both support multi-step retrieval and context packing.
- Both have ingestion pipelines and configurable environment-based behavior.

## Key Differences
- Data domain:
  - SummarizerArchitecture indexes static pattern docs.
  - RSSReader ingests live RSS articles + graphs with ongoing refresh.
- Storage and retrieval:
  - SummarizerArchitecture uses ChromaDB/Elasticsearch/Redis.
  - RSSReader uses Postgres (FTS), Qdrant, and Neo4j for graph queries.
- Orchestration style:
  - SummarizerArchitecture (agentic-pattern-query-app) uses multi-agent specialist roles.
  - RSSReader uses Planner + ResearchAgent with retrieval fusion in a single orchestrator.
- Observability:
  - SummarizerArchitecture includes full Prometheus/Grafana dashboards and quality metrics.
  - RSSReader currently uses loguru and basic OTel setup.
- Citation format:
  - SummarizerArchitecture uses APA-style citations with provenance.
  - RSSReader uses strict markdown link + ID format.
- UI:
  - SummarizerArchitecture has a bespoke web UI (React).
  - RSSReader uses A2UI declarative rendering + SSE/JSONL.

## Common Building Blocks
- FastAPI service layer with JSON APIs.
- Config-driven model/provider selection (Ollama + Gemini).
- Vector retrieval + ranking before synthesis.
- Tool-based retrieval and knowledge augmentation.

## Frameworks, Tools, and Integration Patterns
SummarizerArchitecture:
- Frameworks: Google ADK, FastAPI.
- Tools: ChromaDB, Qdrant, Elasticsearch (BM25), Redis, Prometheus/Grafana, Trafilatura, DuckDuckGo, SentenceTransformers.
- Integration patterns: 7-layer RAG, hybrid retrieval, web KB cache, semantic caching, metrics pipelines, ingestion scripts, Dockerized infra.

RSSReader:
- Frameworks: FastAPI, ADK shim via google-genai, A2UI.
- Tools: Postgres, Qdrant, Neo4j, Ollama, optional web search.
- Integration patterns: Topic sessions, planner + retrieval fusion, graph-based retrieval, SSE/JSONL UI streaming.

MCP:
- No MCP usage in SummarizerArchitecture (no MCP references found).
- RSSReader currently does not use MCP either.

## Recommended Reuse Plan (High Impact)
1) Retrieval fusion upgrades
- Add RRF fusion weights and optional BM25 layer (Elasticsearch or Postgres FTS scoring normalization).
- Implement two-phase embeddings (fast local + premium rerank) to improve precision.

2) Quality + safety layer
- Add quality metrics evaluation (faithfulness, relevancy, hallucination flags) in responses.
- Introduce a Verification agent role before final answer.

3) Caching and performance
- Add semantic cache keyed by normalized query and session context (Redis-backed).
- Reuse incremental embedding hashing to avoid re-embedding unchanged articles.

4) Observability
- Extend current OTel/loguru with Prometheus metrics and Grafana dashboards.
- Track retrieval latency, model latency, citation compliance, cache hit rate.

5) External context
- Port web-knowledge-base workflow for topic updates and low-confidence queries.

## Architecture Pattern Differences (Conceptual)
- SummarizerArchitecture is a “document-store-first” design with layered retrieval, strong observability, and evaluation baked in.
- RSSReader is a “live-content-first” design with topic sessions, graph search, and adaptive UI outputs (A2UI).
- The best combined architecture is: RSSReader’s live ingestion + graph context + A2UI, layered with SummarizerArchitecture’s hybrid retrieval, verification, and telemetry.

## Notes
- The strongest synergy is adopting semantic-pattern-query-app’s telemetry/metrics and hybrid retrieval stack while keeping RSSReader’s graph and session memory.
- Agentic-pattern-query-app’s specialist roles map cleanly to RSSReader’s planner + retrieval + synthesis pipeline and can be used to improve reliability.

