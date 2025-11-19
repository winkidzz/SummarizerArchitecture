# Semantic Pattern Query App

Production-ready RAG system with **dual performance optimizations** for querying the Healthcare AI Pattern Library.

## Key Features

- **Two-Phase Hybrid RAG**: Local embeddings (384D) for Phase 1 broad search, premium embeddings (768D Ollama/Gemini) for Phase 2 precise re-ranking
- **Multi-Embedder Support**: Switch between Ollama and Gemini embeddings via configuration
- **Hash-Based Incremental Re-Embedding**: Skip unchanged documents using SHA256 comparison
- **Production Architecture**: 7-layer system with vector search, BM25, reranking, and semantic caching
- **Real-Time Quality Metrics**: Automatic hallucination detection and quality monitoring on every query
- **100% Open Source Stack**: Qdrant, Elasticsearch, Redis, Ollama, Sentence Transformers

## Quick Start

### Startup Sequence

**Scripts must be started in this order:**

#### 1. **Prerequisites** (One-time setup)

```bash
cd semantic-pattern-query-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull nomic-embed-text   # Embedding model
ollama pull qwen3:14b          # Generation model

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

**Required configuration** in `.env`:
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `OLLAMA_MODEL=nomic-embed-text` - Embedding model
- `OLLAMA_GENERATION_MODEL=qwen3:14b` - Generation model
- `QUERY_EMBEDDER_TYPE=ollama` - Default embedder ("ollama" or "gemini")

#### 2. **Start Infrastructure Services** (Always first)

```bash
# Start Docker services
docker-compose up -d
```

This starts:
- **Elasticsearch** (BM25 search) - Port 9200, 9300
- **Qdrant** (vector DB) - Port 6333, 6334
- **Redis** (caching) - Port 6380
- **Prometheus** (metrics) - Port 9090
- **Grafana** (dashboards) - Port 3333

Wait ~15 seconds for services to become healthy.

#### 3. **Ingest Documents** (One-time or when patterns update)

```bash
# Ingest pattern library
python scripts/ingest_patterns.py

# Optional: Calibrate embeddings for cross-space mapping
python scripts/calibrate_embeddings.py
```

#### 4. **Start API Server** (Always after Docker services)

```bash
# Start the API server
./scripts/start-server.sh
```

Server runs at http://localhost:8000 - Visit http://localhost:8000/docs for API documentation.

#### 5. **Start Web UI** (Optional)

```bash
cd web-ui
npm install              # First time only
npm run dev
```

Open http://localhost:5173 - The UI requires the API server to be running.

### Daily Workflow

**Most common usage** (after initial setup):

```bash
# Quick Start - One command (skip ingestion if already done)
./scripts/start-all.sh --skip-ingest

# Work with the system...

# Quick Stop - One command
./scripts/stop-all.sh
```

**Manual approach** (for more control):

```bash
# Start
docker-compose up -d              # Start infrastructure
./scripts/start-server.sh         # Start API server

# Work with the system...

# Stop
./scripts/stop-server.sh          # Stop API server
docker-compose down               # Optional: stop infrastructure
```

### Complete Startup Script

**Option 1: One-command startup** (recommended):

```bash
# Start everything (includes document ingestion)
./scripts/start-all.sh

# Start everything (skip ingestion if already done)
./scripts/start-all.sh --skip-ingest
```

**Option 2: Manual startup** (for more control):

```bash
# Start infrastructure
docker-compose up -d
sleep 15

# Ingest documents (skip if already done)
python scripts/ingest_patterns.py

# Start API server
./scripts/start-server.sh
```

## Quick Access Links

Once all services are running:

- **Web UI**: http://localhost:5173
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Metrics Endpoint**: http://localhost:8000/metrics
- **Grafana Dashboards**: http://localhost:3333 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Elasticsearch**: http://localhost:9200
- **Qdrant**: http://localhost:6333/dashboard

See [docs/PORTS.md](docs/PORTS.md) for complete port configuration.

### Shutdown Sequence

**Option 1: One-command shutdown** (recommended):

```bash
# Stop all services (API, Web UI, Docker)
./scripts/stop-all.sh
```

**Option 2: Manual shutdown** (for more control):

```bash
# 1. Stop Web UI (Ctrl+C in terminal)

# 2. Stop API server
./scripts/stop-server.sh

# 3. Stop Docker services (optional)
docker-compose down
```

### Cleanup and Maintenance

**Clean cache and logs** (keeps indexed data):

```bash
./scripts/clean-all.sh
```

**Full cleanup** (WARNING: Deletes all indexed data):

```bash
./scripts/clean-all.sh --full
```

After full cleanup, you'll need to re-ingest documents:

```bash
./scripts/start-all.sh  # Automatically re-ingests
```

### Available Scripts

#### Main Management Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/start-all.sh` | **Start all services** (Docker + API) | Daily startup |
| `scripts/stop-all.sh` | **Stop all services** | Daily shutdown |
| `scripts/clean-all.sh` | **Clean cache/logs** | Maintenance |
| `scripts/clean-all.sh --full` | **Full cleanup** (deletes data) | Reset system |

#### Individual Service Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/start-server.sh` | Start API server only | Manual control |
| `scripts/stop-server.sh` | Stop API server only | Manual control |
| `scripts/ingest_patterns.py` | Load pattern documents | Once or when patterns update |
| `scripts/calibrate_embeddings.py` | Calibrate cross-space mapping | Once or when switching embedders |
| `scripts/query_example.py` | Test CLI query | After server starts |

#### Monitoring Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/monitoring/setup-monitoring.sh` | Setup monitoring stack | One-time |
| `scripts/monitoring/import_dashboards.sh` | Import Grafana dashboards | One-time or when dashboards update |
| `scripts/monitoring/restart_api_with_metrics.sh` | Restart API with updated code | After code changes |

#### Testing Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/testing/test_embedder_selection.py` | Test embedder switching | Verify embedder config |
| `scripts/testing/test_telemetry.py` | Test telemetry system | Verify metrics collection |

#### Setup Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/setup/setup_env.sh` | Environment setup | Initial setup |
| `scripts/setup/setup_services.sh` | Service configuration | Initial setup |

## Usage Examples

### Query via API

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5
  }'
```

### Query via Python

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query("What is RAPTOR RAG?", top_k=5)

print(result["answer"])
print(f"Sources: {len(result['sources'])}")
```

### Interactive API Docs

Visit http://localhost:8000/docs to try queries in your browser.

### Quality Metrics in Response

Every query now includes **real-time quality metrics**:

```json
{
  "answer": "RAPTOR RAG is a retrieval technique...",
  "sources": [...],
  "quality_metrics": {
    "answer": {
      "faithfulness": 0.95,
      "relevancy": 0.88,
      "completeness": 0.80,
      "has_hallucination": false,
      "hallucination_severity": "minor"
    },
    "context": {
      "relevancy": 0.87,
      "utilization": 0.75
    }
  }
}
```

**What's monitored automatically**:
- ✅ **Hallucination Detection** - Detects fabricated claims not supported by context
- ✅ **Answer Faithfulness** - % of claims supported by retrieved context
- ✅ **Answer Relevancy** - How well answer addresses the query
- ✅ **Context Utilization** - % of retrieved chunks actually used

See [docs/implementation/REAL_TIME_QUALITY_METRICS.md](docs/implementation/REAL_TIME_QUALITY_METRICS.md) for details.

## Architecture

**7-Layer Production RAG System**:

1. **Document Processing**: Multi-stage PDF/markdown extraction with fallbacks
2. **Semantic Chunking**: Structure-aware chunking preserving markdown hierarchy
3. **Hybrid Embedding**: Two-phase strategy (local 384D → premium 768D re-ranking)
4. **Vector Database**: Qdrant with scalar quantization (4x memory reduction)
5. **Hybrid Retrieval**: Vector search + BM25 + RRF + reranking
6. **Context Management**: Token-aware context packing with citations
7. **Semantic Caching**: Redis-based cache for similar queries (40%+ hit rate)

## Dual Performance Optimizations

### 1. Two-Phase Hybrid Embeddings

**Phase 1 - Broad Search** (cost-effective):
- Uses local model (all-MiniLM-L12-v2, 384 dimensions)
- Retrieves top-K candidates (e.g., 50 documents)
- Fast approximate search

**Phase 2 - Precise Re-Ranking** (high-quality):
- Re-embeds top candidates with premium embedder (Ollama/Gemini, 768 dimensions)
- Precise similarity scoring in high-dimensional space
- Returns top results (e.g., 10 documents)

**Benefits**:
- 90%+ cost reduction (only re-embed top candidates)
- Better accuracy from premium embeddings on final ranking
- Configurable via `QUERY_EMBEDDER_TYPE` environment variable

### 2. Hash-Based Incremental Re-Embedding

When switching embedders or re-ingesting:
- Computes SHA256 hash of document content
- Skips re-embedding if content unchanged
- Only processes new/modified documents

**Benefits**:
- 10x faster re-ingestion for unchanged documents
- Seamless embedder switching (Ollama ↔ Gemini)
- Preserves vector DB consistency

## Configuration

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed configuration options.

**Key environment variables**:
- `GEMINI_API_KEY` - Gemini API key
- `OLLAMA_MODEL` - Ollama embedding model (default: nomic-embed-text)
- `OLLAMA_GENERATION_MODEL` - Ollama generation model (default: qwen3:14b)
- `QUERY_EMBEDDER_TYPE` - Default embedder: "ollama" or "gemini"
- `QDRANT_URL` - Qdrant endpoint (default: http://localhost:6333)
- `ELASTICSEARCH_URL` - Elasticsearch endpoint (default: http://localhost:9200)
- `REDIS_HOST` - Redis host (default: localhost)

## Documentation

### Setup & Configuration
- [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md) - Step-by-step setup guide
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md) - Environment variables reference
- [docs/PORTS.md](docs/PORTS.md) - Port assignments and service URLs
- [docs/MONITORING_SETUP.md](docs/MONITORING_SETUP.md) - Prometheus & Grafana setup

### Usage & Features
- [docs/guides/API_GUIDE.md](docs/guides/API_GUIDE.md) - API endpoints and examples
- [docs/guides/QUERY_GUIDE.md](docs/guides/QUERY_GUIDE.md) - Advanced query patterns
- [docs/guides/EMBEDDER_SELECTION_GUIDE.md](docs/guides/EMBEDDER_SELECTION_GUIDE.md) - Choosing embedders
- [docs/guides/EVALUATION_QUICK_START.md](docs/guides/EVALUATION_QUICK_START.md) - Quality metrics evaluation

### Quality Metrics & Monitoring
- [docs/implementation/REAL_TIME_QUALITY_METRICS.md](docs/implementation/REAL_TIME_QUALITY_METRICS.md) - Real-time quality metrics
- [docs/guides/GRAFANA_QUALITY_DASHBOARDS.md](docs/guides/GRAFANA_QUALITY_DASHBOARDS.md) - Quality metrics dashboards
- [docs/guides/QUALITY_METRICS_TROUBLESHOOTING.md](docs/guides/QUALITY_METRICS_TROUBLESHOOTING.md) - Troubleshooting guide
- [docs/guides/TELEMETRY_QUICKSTART.md](docs/guides/TELEMETRY_QUICKSTART.md) - Telemetry setup

### Integration Guides
- [docs/guides/CALIBRATION_GUIDE.md](docs/guides/CALIBRATION_GUIDE.md) - Embedding calibration for cross-space mapping
- [docs/guides/GEMINI_INTEGRATION.md](docs/guides/GEMINI_INTEGRATION.md) - Using Gemini embeddings

### Implementation Details
- [docs/implementation/TELEMETRY_IMPLEMENTATION.md](docs/implementation/TELEMETRY_IMPLEMENTATION.md) - Telemetry system
- [docs/implementation/PERFORMANCE_OPTIMIZATIONS.md](docs/implementation/PERFORMANCE_OPTIMIZATIONS.md) - Performance optimizations
- [docs/implementation/INCREMENTAL_EMBEDDING_OPTIMIZATION.md](docs/implementation/INCREMENTAL_EMBEDDING_OPTIMIZATION.md) - Incremental re-embedding

## Project Structure

```
semantic-pattern-query-app/
├── README.md                    # This file
├── CHANGELOG.md                 # Complete project history
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Service definitions (Qdrant, ES, Redis, Prometheus, Grafana)
├── prometheus.yml               # Prometheus scrape configuration
├── .env.example                 # Configuration template
├── src/
│   ├── api_server.py           # FastAPI server with quality metrics
│   └── document_store/
│       ├── orchestrator.py     # Main orchestrator (7-layer pipeline)
│       ├── processors/         # Document extraction & chunking
│       ├── embeddings/         # Hybrid embedding (local + premium)
│       ├── storage/            # Qdrant vector store
│       ├── search/             # Hybrid retrieval (vector + BM25)
│       ├── generation/         # RAG generation with citations
│       ├── cache/              # Semantic caching (Redis)
│       ├── monitoring/         # Prometheus metrics & telemetry
│       └── evaluation/         # Quality metrics evaluation
├── tests/
│   ├── test_api_quality_metrics.py        # API integration tests
│   ├── test_quality_metrics_standalone.py # Evaluation module tests
│   ├── test_healthcare_evaluation.py      # Healthcare scenario tests
│   ├── test_evaluation_comparison.py      # Comparison tests
│   └── test_optimizations.py              # Performance tests
├── scripts/
│   ├── ingest_patterns.py      # Pattern ingestion
│   ├── query_example.py        # CLI query example
│   ├── calibrate_embeddings.py # Embedding calibration
│   ├── start-server.sh         # Server startup script
│   ├── monitoring/             # Monitoring scripts
│   │   ├── import_dashboards.sh
│   │   ├── restart_api_with_metrics.sh
│   │   └── setup-monitoring.sh
│   ├── testing/                # Test scripts
│   │   ├── test_embedder_selection.py
│   │   └── test_telemetry.py
│   └── setup/                  # Setup scripts
│       ├── setup_env.sh
│       └── setup_services.sh
├── docs/
│   ├── guides/                 # User guides
│   │   ├── QUICKSTART.md
│   │   ├── API_GUIDE.md
│   │   ├── QUERY_GUIDE.md
│   │   ├── EMBEDDER_SELECTION_GUIDE.md
│   │   ├── EVALUATION_QUICK_START.md
│   │   ├── GRAFANA_QUALITY_DASHBOARDS.md
│   │   ├── QUALITY_METRICS_TROUBLESHOOTING.md
│   │   └── [8 more guides]
│   ├── implementation/         # Implementation details
│   │   ├── REAL_TIME_QUALITY_METRICS.md
│   │   ├── TELEMETRY_IMPLEMENTATION.md
│   │   ├── PERFORMANCE_OPTIMIZATIONS.md
│   │   └── [4 more docs]
│   ├── archived/               # Historical documentation
│   ├── CONFIGURATION.md        # Environment variables
│   ├── PORTS.md               # Port assignments
│   └── MONITORING_SETUP.md    # Monitoring setup
├── grafana/
│   ├── dashboards/            # 6 dashboard templates (JSON)
│   │   ├── rag-performance-detailed.json
│   │   ├── rag-system-telemetry.json
│   │   ├── embedder-comparison.json
│   │   ├── rag-system-health.json
│   │   ├── infrastructure-health.json
│   │   └── rag-quality-metrics.json (NEW)
│   └── provisioning/          # Auto-provisioning configs
│       ├── datasources/
│       └── dashboards/
└── web-ui/                    # React dashboard (Vite)
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker status
docker ps

# Check service logs
docker-compose logs qdrant
docker-compose logs elasticsearch
docker-compose logs redis

# Restart services
docker-compose restart
```

### Ollama Connection Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Verify models are available
ollama list

# Pull missing models
ollama pull nomic-embed-text
ollama pull qwen3:14b
```

### Embedding Errors

**"Model does not support embeddings"**:
- Ensure `OLLAMA_MODEL` is set to an embedding model (nomic-embed-text)
- Ensure `OLLAMA_GENERATION_MODEL` is set to a generation model (qwen3:14b)
- Check `.env` configuration matches model capabilities

**Dimension mismatch**:
- See [docs/guides/GEMINI_INTEGRATION.md](docs/guides/GEMINI_INTEGRATION.md) for Gemini-specific issues
- See [docs/guides/CALIBRATION_GUIDE.md](docs/guides/CALIBRATION_GUIDE.md) for cross-space mapping

### API Key Issues

- Copy `.env.example` to `.env`
- Add your Gemini API key to `GEMINI_API_KEY`
- Never commit `.env` to git (protected by .gitignore)

## Related Projects

- [Pattern Library](../pattern-library/) - Healthcare AI architecture blueprints
- [Pattern Query App](../pattern-query-app/) - Alternative implementation using ChromaDB

## Built With

- **Qdrant** - Vector database with scalar quantization
- **Elasticsearch** - BM25 keyword search
- **Redis** - Semantic caching layer
- **Ollama** - Local LLM inference (Qwen models)
- **Google Gemini** - Premium embeddings (optional)
- **Sentence Transformers** - Local embedding models
- **FastAPI** - REST API framework

---

**Part of the AI Summarization Reference Architecture project**
