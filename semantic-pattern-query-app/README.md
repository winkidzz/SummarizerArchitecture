# Semantic Pattern Query App

Production-ready RAG system with **dual performance optimizations** for querying the Healthcare AI Pattern Library.

## Key Features

- **Two-Phase Hybrid RAG**: Local embeddings (384D) for Phase 1 broad search, premium embeddings (768D Ollama/Gemini) for Phase 2 precise re-ranking
- **Multi-Embedder Support**: Switch between Ollama and Gemini embeddings via configuration
- **Hash-Based Incremental Re-Embedding**: Skip unchanged documents using SHA256 comparison
- **Production Architecture**: 7-layer system with vector search, BM25, reranking, and semantic caching
- **100% Open Source Stack**: Qdrant, Elasticsearch, Redis, Ollama, Sentence Transformers

## Quick Start

### 1. Setup Services

```bash
cd semantic-pattern-query-app
docker-compose up -d
```

This starts Qdrant (vector DB), Elasticsearch (BM25), and Redis (caching).

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

**Required configuration**:
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `OLLAMA_MODEL=nomic-embed-text` - For embeddings (must support embeddings)
- `OLLAMA_GENERATION_MODEL=qwen3:14b` - For text generation
- `QUERY_EMBEDDER_TYPE=ollama` - Default embedder ("ollama" or "gemini")

See [.env.example](.env.example) for all options.

### 3. Install Dependencies & Setup Ollama

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull nomic-embed-text   # Embedding model
ollama pull qwen3:14b          # Generation model
```

### 4. Ingest Pattern Library

```bash
python scripts/ingest_patterns.py
```

This processes all markdown files from `../pattern-library/` and creates embeddings.

### 5. Start API Server

```bash
./venv/bin/python3 src/api_server.py
```

Server runs at http://localhost:8000

Visit http://localhost:8000/docs for interactive API documentation.

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

- [QUICKSTART.md](docs/QUICKSTART.md) - Step-by-step setup guide
- [API_GUIDE.md](docs/API_GUIDE.md) - API endpoints and examples
- [CONFIGURATION.md](docs/CONFIGURATION.md) - Environment variables reference
- [CALIBRATION_GUIDE.md](docs/CALIBRATION_GUIDE.md) - Embedding calibration for cross-space mapping
- [GEMINI_INTEGRATION.md](docs/GEMINI_INTEGRATION.md) - Using Gemini embeddings
- [QUERY_GUIDE.md](docs/QUERY_GUIDE.md) - Advanced query patterns

## Project Structure

```
semantic-pattern-query-app/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── docker-compose.yml            # Service definitions
├── .env.example                 # Configuration template
├── src/
│   └── document_store/
│       ├── orchestrator.py      # Main orchestrator
│       ├── embeddings/          # Hybrid embedding layer
│       ├── storage/             # Qdrant vector store
│       ├── search/              # Hybrid retrieval
│       ├── generation/          # RAG generation
│       └── cache/               # Semantic caching
├── scripts/
│   ├── ingest_patterns.py       # Pattern ingestion
│   └── query_example.py         # CLI query example
└── docs/                        # Documentation
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
- See [docs/GEMINI_INTEGRATION.md](docs/GEMINI_INTEGRATION.md) for Gemini-specific issues
- See [docs/CALIBRATION_GUIDE.md](docs/CALIBRATION_GUIDE.md) for cross-space mapping

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
