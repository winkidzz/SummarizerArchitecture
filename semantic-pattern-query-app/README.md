# Semantic Pattern Query App

**Production-ready RAG system implementing the complete 7-layer architecture for querying the Healthcare AI Pattern Library.**

This application implements a production-grade Retrieval-Augmented Generation (RAG) system using 100% open-source components and Ollama Qwen models. It follows the architecture documented in `pattern-query-app/docs/RAG Architecture.md`.

## 🏗️ Architecture

The system implements 7 layers:

1. **Document Processing**: Multi-stage extraction with fallbacks (pypdf → pdfplumber)
2. **Semantic Chunking**: Structure-aware chunking preserving markdown structure
3. **Hybrid Embedding**: Local model for indexing + Qwen for queries and re-embedding
4. **Vector Database**: Qdrant with scalar quantization (4x memory reduction)
5. **Hybrid Retrieval**: Two-step vector search + BM25 + RRF + reranking
6. **Context Management**: Intelligent context packing with citations
7. **Semantic Caching**: Redis-based cache for similar queries

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Ollama installed and running
- 8GB+ RAM recommended

### 1. Setup Services

Start all required services (Qdrant, Elasticsearch, Redis):

```bash
cd semantic-pattern-query-app
./scripts/setup_services.sh
```

Or manually:

```bash
docker-compose up -d
```

### 2. Setup Ollama

Make sure Ollama is running and pull the Qwen model:

```bash
# Start Ollama (if not running)
ollama serve

# Pull Qwen model
ollama pull qwen3:14b
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest Pattern Library

Ingest all patterns from the pattern-library directory:

```bash
python scripts/ingest_patterns.py
```

This will:
- Extract all markdown files from `../pattern-library/`
- Chunk them semantically
- Generate embeddings (local model for indexing)
- Store in Qdrant and Elasticsearch

### 5. Query the System

**CLI:**
```bash
python scripts/query_example.py "What is RAPTOR RAG?"
```

**API Server:**
```bash
python src/api_server.py
# Then visit http://localhost:8000/docs for API documentation
```

**Python:**
```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query("What is RAPTOR RAG?", top_k=5)
print(result["answer"])
```

## 📁 Project Structure

```
semantic-pattern-query-app/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                  # Service definitions
├── src/
│   └── document_store/
│       ├── orchestrator.py            # Main orchestration layer
│       ├── processors/
│       │   ├── robust_extractor.py    # Layer 1: Multi-stage extraction
│       │   └── semantic_chunker.py   # Layer 2: Structure-aware chunking
│       ├── embeddings/
│       │   ├── hybrid_embedder.py     # Layer 3: Hybrid embedding strategy
│       │   └── qwen_embedder.py       # Ollama Qwen embedding wrapper
│       ├── storage/
│       │   └── qdrant_store.py        # Layer 4: Qdrant vector store
│       ├── search/
│       │   ├── hybrid_retriever.py   # Layer 5: Hybrid retrieval orchestration
│       │   ├── bm25_search.py        # Elasticsearch BM25 integration
│       │   └── two_step_retrieval.py # Two-step vector search
│       ├── generation/
│       │   └── rag_generator.py      # Layer 6: Context management & generation
│       ├── cache/
│       │   └── semantic_cache.py     # Layer 7: Semantic caching
│       └── api_server.py             # FastAPI REST API
├── scripts/
│   ├── ingest_patterns.py            # Ingest pattern-library directory
│   ├── setup_services.sh              # Setup Elasticsearch, Qdrant, Redis
│   └── query_example.py               # CLI query example
└── examples/
    └── query_patterns.py              # Usage examples
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:14b

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=pattern_documents

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX_NAME=pattern_documents

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=3600
CACHE_SIMILARITY_THRESHOLD=0.92

# Data Source
PATTERN_LIBRARY_PATH=../pattern-library
```

### Service URLs

- **Qdrant**: http://localhost:6333
- **Elasticsearch**: http://localhost:9200
- **Redis**: localhost:6379
- **API Server**: http://localhost:8000

## 📊 Features

### Production-Ready Architecture

- ✅ **Multi-stage extraction**: Handles PDFs, markdown, and text files
- ✅ **Semantic chunking**: Preserves document structure and context
- ✅ **Hybrid embeddings**: Cost-optimized two-step strategy
- ✅ **Quantized storage**: 4x memory reduction with Qdrant
- ✅ **Hybrid retrieval**: Combines semantic and keyword search
- ✅ **Intelligent context**: Smart token management and citations
- ✅ **Semantic caching**: 40%+ cache hit rate for similar queries

### Performance Targets

- **Average latency**: <500ms
- **Retrieval recall@10**: >85%
- **Cache hit rate**: >40%
- **Memory usage**: <12GB (with quantization)

## 🔍 Usage Examples

### Basic Query

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query("What is RAPTOR RAG?", top_k=5)

print(result["answer"])
print(f"Sources: {len(result['sources'])}")
print(f"Cache hit: {result['cache_hit']}")
```

### Ingest Custom Documents

```python
orchestrator = SemanticPatternOrchestrator()

# Ingest a single document
orchestrator.ingest_document("path/to/document.md")

# Ingest a directory
orchestrator.ingest_directory("path/to/documents", pattern="**/*.md")
```

### API Usage

Start the API server:

```bash
python src/api_server.py
```

Query via HTTP:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAPTOR RAG?", "top_k": 5}'
```

## 🧪 Testing

### Check Service Health

```bash
# Qdrant
curl http://localhost:6333/health

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Redis
redis-cli ping

# API
curl http://localhost:8000/health
```

### Get System Stats

```python
orchestrator = SemanticPatternOrchestrator()
stats = orchestrator.get_stats()
print(stats)
```

## 🐛 Troubleshooting

### Quick Reference

For detailed troubleshooting guides, see:
- **[Troubleshooting Index](docs/TROUBLESHOOTING_INDEX.md)** - Quick reference to all troubleshooting docs
- **[Gemini Embedding Issues](docs/GEMINI_EMBEDDING_TROUBLESHOOTING.md)** - Dimension mismatch, batch handling, array shape errors
- **[Gemini Integration Guide](GEMINI_INTEGRATION.md)** - Setup and configuration
- **[Calibration Guide](CALIBRATION_GUIDE.md)** - Embedding calibration mapping
- **[Environment Setup](ENV_SETUP.md)** - API keys and configuration

### Common Issues

#### Services Not Starting

```bash
# Check Docker is running
docker ps

# Check service logs
docker-compose logs qdrant
docker-compose logs elasticsearch
docker-compose logs redis

# Restart services
docker-compose restart
```

#### Ollama Connection Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Verify model is available
ollama list

# Pull model if missing
ollama pull qwen3:14b
```

#### Embedding Errors

If you encounter embedding dimension mismatches:

1. Check that the local embedding model matches the Qdrant vector size
2. Verify Qwen model supports embeddings (some models may not)
3. Check alignment matrix if using two-step retrieval
4. **For Gemini**: See [Gemini Embedding Troubleshooting](docs/GEMINI_EMBEDDING_TROUBLESHOOTING.md)

#### Memory Issues

- Enable Qdrant quantization (already enabled by default)
- Reduce `top_k_approximate` in retrieval
- Use smaller embedding models
- Increase Docker memory limits

## 📚 Architecture Details

### Layer 1: Document Processing

Multi-stage extraction with confidence scoring:
- **Stage 1**: Fast extraction (pypdf) - confidence > 0.85
- **Stage 2**: Table-aware extraction (pdfplumber) - confidence > 0.75
- **Fallback**: Basic extraction with lower confidence

### Layer 2: Semantic Chunking

Structure-aware chunking:
- Detects markdown sections (headers, code blocks)
- Preserves atomic sections
- Adds overlap only when needed
- Respects sentence boundaries

### Layer 3: Hybrid Embedding

Cost-optimized strategy:
- **Bulk indexing**: Local model (all-MiniLM-L12-v2) - FREE
- **Queries**: Ollama Qwen embeddings - low volume
- **Re-embedding**: Top candidates with Qwen for precision

### Layer 4: Vector Database

Qdrant configuration:
- Scalar quantization (int8) - 4x memory reduction
- On-disk storage for large datasets
- Payload filtering for metadata queries

### Layer 5: Hybrid Retrieval

Multi-stage retrieval:
1. Two-step vector search (local approximate + Qwen re-embedding)
2. BM25 keyword search (Elasticsearch)
3. Reciprocal Rank Fusion (RRF)
4. Cross-encoder reranking

### Layer 6: Context Management

Intelligent context packing:
- Respects token limits (8000 tokens default)
- Prioritizes high-scoring documents
- Tracks citations
- Structured prompt building

### Layer 7: Semantic Caching

Redis-based cache:
- Cosine similarity matching (threshold: 0.92)
- TTL management (1 hour default)
- Context-aware cache keys

## 🔗 Related Projects

- **[Pattern Library](../pattern-library/)**: The documentation this app queries
- **[Pattern Query App](../pattern-query-app/)**: Alternative implementation using ChromaDB and ADK

## 📝 License

Part of the AI Summarization Reference Architecture project. See root README for license.

## 🤝 Contributing

Contributions welcome! Areas of focus:
- Performance optimizations
- Additional document formats
- Improved reranking models
- Monitoring and observability

---

**Built with**: Qdrant, Elasticsearch, Redis, Ollama, Sentence Transformers, FastAPI

