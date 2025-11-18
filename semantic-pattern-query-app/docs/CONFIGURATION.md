# Configuration Reference

Complete reference for all environment variables and configuration options.

## Environment Variables

All configuration is managed via `.env` file. Copy `.env.example` to `.env` and customize.

### Required Configuration

#### API Keys

**GEMINI_API_KEY**
- **Description**: Google Gemini API key for premium embeddings
- **Required**: Yes (if using Gemini embedder)
- **Default**: None
- **Get key**: https://makersuite.google.com/app/apikey
- **Example**: `AIzaSyBneZu4ShIXR6mXiSAfD5FPJcnbx-vLpoc`

```bash
GEMINI_API_KEY=your-api-key-here
```

### Embedding Models

**GEMINI_EMBEDDING_MODEL**
- **Description**: Gemini embedding model identifier
- **Required**: No
- **Default**: `models/embedding-001`
- **Dimensions**: 768
- **Use case**: Premium embedding for precise similarity scoring

```bash
GEMINI_EMBEDDING_MODEL=models/embedding-001
```

**OLLAMA_MODEL**
- **Description**: Ollama embedding model name
- **Required**: Yes (if using Ollama embedder)
- **Default**: `nomic-embed-text`
- **Dimensions**: 768 (nomic-embed-text)
- **Important**: Must be an **embedding model**, not a chat model
- **Use case**: Local embedding for cost-effective querying

```bash
OLLAMA_MODEL=nomic-embed-text
```

**OLLAMA_GENERATION_MODEL**
- **Description**: Ollama generation/chat model for RAG text generation
- **Required**: Yes
- **Default**: `qwen3:14b`
- **Important**: Must be a **generation model**, not an embedding model
- **Use case**: Generating answers from retrieved context

```bash
OLLAMA_GENERATION_MODEL=qwen3:14b
```

**OLLAMA_BASE_URL**
- **Description**: Ollama API endpoint
- **Required**: No
- **Default**: `http://localhost:11434`
- **Use case**: Connect to Ollama service

```bash
OLLAMA_BASE_URL=http://localhost:11434
```

**QUERY_EMBEDDER_TYPE**
- **Description**: Default embedder for queries
- **Required**: No
- **Default**: `ollama`
- **Options**: `ollama`, `gemini`
- **Use case**: Switch between local (Ollama) and premium (Gemini) embeddings

```bash
QUERY_EMBEDDER_TYPE=ollama  # or "gemini"
```

### Service URLs

**QDRANT_URL**
- **Description**: Qdrant vector database endpoint
- **Required**: Yes
- **Default**: `http://localhost:6333`
- **Use case**: Vector similarity search

```bash
QDRANT_URL=http://localhost:6333
```

**ELASTICSEARCH_URL**
- **Description**: Elasticsearch endpoint for BM25 keyword search
- **Required**: Yes
- **Default**: `http://localhost:9200`
- **Use case**: Keyword-based retrieval

```bash
ELASTICSEARCH_URL=http://localhost:9200
```

**REDIS_HOST**
- **Description**: Redis host for semantic caching
- **Required**: No (caching is optional)
- **Default**: `localhost`

```bash
REDIS_HOST=localhost
```

**REDIS_PORT**
- **Description**: Redis port
- **Required**: No
- **Default**: `6380`
- **Note**: Default docker-compose uses 6380 to avoid conflicts

```bash
REDIS_PORT=6380
```

### Data Paths

**PATTERN_LIBRARY_PATH**
- **Description**: Path to pattern library documents
- **Required**: No
- **Default**: `../pattern-library`
- **Use case**: Location of markdown files to ingest

```bash
PATTERN_LIBRARY_PATH=../pattern-library
```

**EMBEDDING_ALIGNMENT_MATRIX_PATH**
- **Description**: Path to calibration matrix for embedding space mapping
- **Required**: No (used for cross-space calibration)
- **Default**: `alignment_matrix.npy`
- **Use case**: Map premium embeddings to local embedding space

```bash
EMBEDDING_ALIGNMENT_MATRIX_PATH=alignment_matrix.npy
```

**EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI**
- **Description**: Gemini-specific calibration matrix
- **Required**: No
- **Default**: `alignment_matrix_gemini.npy`

```bash
EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI=alignment_matrix_gemini.npy
```

**EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA**
- **Description**: Ollama-specific calibration matrix
- **Required**: No
- **Default**: `alignment_matrix_ollama.npy`

```bash
EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA=alignment_matrix_ollama.npy
```

### Optional Advanced Configuration

**LOCAL_EMBEDDING_MODEL**
- **Description**: Local Sentence Transformer model for bulk indexing
- **Required**: No
- **Default**: `all-MiniLM-L12-v2`
- **Dimensions**: 384
- **Use case**: Phase 1 approximate search (cost-free)

```bash
LOCAL_EMBEDDING_MODEL=all-MiniLM-L12-v2
```

**API_HOST**
- **Description**: FastAPI server host
- **Required**: No
- **Default**: `0.0.0.0` (all interfaces)

```bash
API_HOST=0.0.0.0
```

**API_PORT**
- **Description**: FastAPI server port
- **Required**: No
- **Default**: `8000`

```bash
API_PORT=8000
```

**LOG_LEVEL**
- **Description**: Logging level
- **Required**: No
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

```bash
LOG_LEVEL=INFO
```

## Configuration Scenarios

### Scenario 1: Ollama Only (Cost-Free)

```bash
# Use Ollama for both embeddings and generation
QUERY_EMBEDDER_TYPE=ollama
OLLAMA_MODEL=nomic-embed-text
OLLAMA_GENERATION_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434

# No Gemini API key required
# GEMINI_API_KEY=

# Services
QDRANT_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6380

# Data
PATTERN_LIBRARY_PATH=../pattern-library
```

### Scenario 2: Gemini Premium Embeddings

```bash
# Use Gemini for query embeddings (premium quality)
QUERY_EMBEDDER_TYPE=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_EMBEDDING_MODEL=models/embedding-001

# Use Ollama for text generation (cost-free)
OLLAMA_GENERATION_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434

# Services
QDRANT_URL=http://localhost:6333
ELASTICSEARCH_URL=http://localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6380

# Data
PATTERN_LIBRARY_PATH=../pattern-library
```

### Scenario 3: Remote Services

```bash
# Remote Ollama instance
OLLAMA_BASE_URL=http://ollama-server.company.com:11434

# Remote Qdrant cluster
QDRANT_URL=http://qdrant-cluster.company.com:6333

# Remote Elasticsearch
ELASTICSEARCH_URL=http://elastic.company.com:9200

# Remote Redis
REDIS_HOST=redis.company.com
REDIS_PORT=6379

# Custom data path
PATTERN_LIBRARY_PATH=/mnt/shared/pattern-library
```

## Important Notes

### Embedding vs Generation Models

**Critical**: Ollama uses separate models for different purposes:

- **OLLAMA_MODEL** (embedding): Must support `.embed()` API
  - Examples: `nomic-embed-text`, `mxbai-embed-large`
  - Used for: Converting queries to vectors

- **OLLAMA_GENERATION_MODEL** (generation): Must support `.generate()` API
  - Examples: `qwen3:14b`, `llama3:8b`, `mistral:7b`
  - Used for: Generating answers from retrieved context

**Common Error**: Using a chat model for `OLLAMA_MODEL` will fail with:
```
"this model does not support embeddings"
```

### Two-Phase Hybrid RAG

The system uses a **two-phase embedding strategy**:

1. **Phase 1 - Approximate Search** (local model):
   - Model: `LOCAL_EMBEDDING_MODEL` (all-MiniLM-L12-v2, 384D)
   - Purpose: Fast, cost-free bulk search
   - Retrieves: Top-K candidates (e.g., 50 documents)

2. **Phase 2 - Precise Re-Ranking** (premium model):
   - Model: `OLLAMA_MODEL` or `GEMINI_EMBEDDING_MODEL` (768D)
   - Purpose: High-quality similarity scoring
   - Re-ranks: Top candidates, returns best results (e.g., 10 documents)

**Configuration Impact**:
- `QUERY_EMBEDDER_TYPE=ollama` → Phase 2 uses Ollama (free, local)
- `QUERY_EMBEDDER_TYPE=gemini` → Phase 2 uses Gemini (premium, cloud)

### Switching Embedders

You can switch between Ollama and Gemini embedders:

1. Update `.env`:
   ```bash
   QUERY_EMBEDDER_TYPE=gemini  # or "ollama"
   ```

2. Restart server:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ./venv/bin/python3 src/api_server.py
   ```

3. **No re-ingestion needed** - The system uses hash-based incremental re-embedding to skip unchanged documents.

### Security Best Practices

1. **Never commit `.env`** - It's in `.gitignore`
2. **Use `.env.example`** - Template without secrets
3. **Rotate API keys** - Regularly update Gemini API key
4. **Restrict access** - Bind API to `127.0.0.1` in production if not public
5. **Use HTTPS** - In production, use reverse proxy (nginx) with TLS

## Validation

### Check Configuration

```bash
# Verify environment variables are loaded
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OLLAMA_MODEL:', os.getenv('OLLAMA_MODEL'))
print('OLLAMA_GENERATION_MODEL:', os.getenv('OLLAMA_GENERATION_MODEL'))
print('QUERY_EMBEDDER_TYPE:', os.getenv('QUERY_EMBEDDER_TYPE'))
"
```

### Test Services

```bash
# Qdrant
curl http://localhost:6333/health

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Redis
docker exec -it semantic-pattern-query-app-redis-1 redis-cli ping

# Ollama
curl http://localhost:11434/api/tags
```

### Verify Models

```bash
# Check Ollama models are available
ollama list | grep nomic-embed-text
ollama list | grep qwen3

# Pull if missing
ollama pull nomic-embed-text
ollama pull qwen3:14b
```

## Troubleshooting

### "Model does not support embeddings"

**Cause**: `OLLAMA_MODEL` is set to a generation model

**Fix**:
```bash
# Correct configuration
OLLAMA_MODEL=nomic-embed-text          # Embedding model
OLLAMA_GENERATION_MODEL=qwen3:14b      # Generation model
```

### Gemini API Key Errors

**Cause**: Invalid or missing API key

**Fix**:
1. Get API key: https://makersuite.google.com/app/apikey
2. Update `.env`: `GEMINI_API_KEY=your-key-here`
3. Restart server

### Connection Refused Errors

**Cause**: Services not running or wrong URLs

**Fix**:
1. Start services: `docker-compose up -d`
2. Check URLs in `.env` match running services
3. Verify with health checks (see above)

## Reference

- [.env.example](../.env.example) - Template configuration
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [API_GUIDE.md](API_GUIDE.md) - API usage
- [README.md](../README.md) - Main documentation

---

**Next**: See [GEMINI_INTEGRATION.md](GEMINI_INTEGRATION.md) for Gemini-specific configuration
