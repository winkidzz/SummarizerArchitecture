# Quick Start Guide

Get the Semantic Pattern Query App running in 5 steps.

## Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose** (for Qdrant, Elasticsearch, Redis)
- **Ollama** (for local LLM inference)
- **8GB+ RAM** recommended

## Step 1: Start Services

Start Qdrant (vector DB), Elasticsearch (BM25), and Redis (caching):

```bash
cd semantic-pattern-query-app
docker-compose up -d
```

**Verify services are running:**

```bash
# Qdrant
curl http://localhost:6333/health

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Redis
docker ps | grep redis
```

## Step 2: Configure Environment

Copy the example configuration and add your API keys:

```bash
cp .env.example .env
```

**Edit `.env` and configure**:

```bash
# Required: Get your Gemini API key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-api-key-here

# Ollama models (default values work)
OLLAMA_MODEL=nomic-embed-text          # Embedding model
OLLAMA_GENERATION_MODEL=qwen3:14b      # Generation/chat model
OLLAMA_BASE_URL=http://localhost:11434

# Default embedder: "ollama" or "gemini"
QUERY_EMBEDDER_TYPE=ollama

# Service URLs (defaults should work)
QDRANT_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6380

# Pattern library path
PATTERN_LIBRARY_PATH=../pattern-library
```

**Important**:
- `OLLAMA_MODEL` must be an **embedding model** (nomic-embed-text)
- `OLLAMA_GENERATION_MODEL` must be a **generation model** (qwen3:14b)
- These are separate models with different purposes

## Step 3: Install Dependencies & Setup Ollama

### Create Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Pull Ollama Models

Make sure Ollama is running, then pull the required models:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull embedding model
ollama pull nomic-embed-text

# Pull generation model
ollama pull qwen3:14b
```

**Verify models are available:**

```bash
ollama list
```

You should see both `nomic-embed-text` and `qwen3:14b` in the list.

## Step 4: Ingest Pattern Library

Process all pattern documents and create embeddings:

```bash
python scripts/ingest_patterns.py
```

**What this does**:
- Scans `../pattern-library/` for markdown files
- Extracts and chunks documents semantically
- Generates embeddings using local model (all-MiniLM-L12-v2)
- Stores in Qdrant (vector search) and Elasticsearch (keyword search)

**Expected output**:
```
Processing pattern-library...
Found 113 markdown files
Ingesting documents...
Progress: 100%|████████████████████| 113/113 [02:15<00:00,  1.19s/file]
Successfully ingested 113 files, 2450 chunks
```

## Step 5: Start API Server

```bash
./venv/bin/python3 src/api_server.py
```

**Server output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Server is now running at:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Try Your First Query

### Option 1: Interactive API Docs (Easiest)

1. Open browser: http://localhost:8000/docs
2. Click on `/query` endpoint
3. Click "Try it out"
4. Enter query:
   ```json
   {
     "query": "What is RAPTOR RAG?",
     "top_k": 5
   }
   ```
5. Click "Execute"
6. See the answer with sources!

### Option 2: Command Line

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5
  }'
```

### Option 3: Python Script

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()
result = orchestrator.query("What is RAPTOR RAG?", top_k=5)

print("Answer:", result["answer"])
print(f"Sources: {len(result['sources'])}")
print(f"Cache hit: {result['cache_hit']}")
```

## Example Queries to Try

### RAG Patterns
- "What is RAPTOR RAG?"
- "Explain hybrid retrieval"
- "How does semantic chunking work?"
- "What is contextual retrieval?"

### Healthcare Use Cases
- "How to summarize patient records?"
- "What are best practices for clinical note generation?"
- "Medical imaging with RAG"

### Vendor Guides
- "How to use LangChain for RAG?"
- "Azure OpenAI implementation guide"
- "AWS Bedrock for healthcare"

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker --version

# Check if ports are available
lsof -ti:6333  # Qdrant
lsof -ti:9200  # Elasticsearch
lsof -ti:6380  # Redis

# Restart services
docker-compose restart
```

### Ollama Connection Failed

```bash
# Start Ollama (if not running)
ollama serve

# Check connection
curl http://localhost:11434/api/tags

# Verify models
ollama list
```

### "Model does not support embeddings" Error

**Cause**: Wrong model assigned to `OLLAMA_MODEL` in `.env`

**Fix**: Ensure `.env` has:
```bash
OLLAMA_MODEL=nomic-embed-text          # Must be embedding model
OLLAMA_GENERATION_MODEL=qwen3:14b      # Must be generation model
```

### Ingestion Fails

```bash
# Check pattern library exists
ls ../pattern-library/

# Check write permissions for Qdrant/Elasticsearch
docker-compose logs qdrant
docker-compose logs elasticsearch

# Try force re-ingest
python scripts/ingest_patterns.py --force
```

### API Returns Empty Results

**Possible causes**:
1. No documents ingested - run `python scripts/ingest_patterns.py`
2. Embedder mismatch - check `QUERY_EMBEDDER_TYPE` in `.env`
3. Qdrant not connected - check `curl http://localhost:6333/health`

**Check system stats:**
```bash
curl http://localhost:8000/stats
```

This should show:
- `points_count` > 0 (documents in Qdrant)
- `embedding_models` configured correctly

## Next Steps

- [API Guide](API_GUIDE.md) - Learn all API endpoints
- [Configuration Reference](CONFIGURATION.md) - Detailed environment variables
- [Gemini Integration](GEMINI_INTEGRATION.md) - Use Gemini embeddings
- [Calibration Guide](CALIBRATION_GUIDE.md) - Advanced embedding mapping
- [Query Guide](QUERY_GUIDE.md) - Advanced query patterns

## Health Check

Verify everything is working:

```bash
# Check all services
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "services": {
    "qdrant": "connected",
    "elasticsearch": "connected",
    "redis": "connected",
    "ollama": "connected"
  },
  "stats": {
    "qdrant": {
      "points_count": 2450
    }
  }
}
```

If all services show "connected" and points_count > 0, you're ready to query!

---

**Need help?** Check the [main README](../README.md) or [Troubleshooting](../README.md#troubleshooting) section.
