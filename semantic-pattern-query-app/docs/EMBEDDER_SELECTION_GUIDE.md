# Embedder Selection Guide

## Overview

The Semantic Pattern Query App supports dynamic embedder selection, allowing you to choose between **Ollama** (local/free) and **Gemini** (cloud/premium) embeddings on a per-query basis.

## Architecture

The system uses a **two-step hybrid embedding strategy** with calibration matrices:

1. **Document Indexing**: All documents are embedded using a fast local model (`all-MiniLM-L12-v2`)
2. **Query Embedding**: Queries can use either Ollama or Gemini embeddings
3. **Calibration**: Premium embeddings are mapped to local space using calibration matrices
4. **Retrieval**: Hybrid retrieval combines vector search and BM25

### Why Calibration Matrices?

Premium embedders (Ollama/Gemini) produce embeddings in a different vector space (768 dimensions) than the local model (384 dimensions). Calibration matrices map premium embeddings to the local space, enabling:

- **Cost optimization**: Bulk document indexing uses free local embeddings
- **Quality queries**: Premium embeddings for better query understanding
- **Flexible switching**: Choose embedder per query without re-indexing

## Setup

### 1. Generate Calibration Matrices

Run the calibration script once to create alignment matrices:

```bash
cd /Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app
./venv/bin/python scripts/calibrate_embeddings.py
```

This generates:
- `alignment_matrix_ollama.npy` (768x384 mapping matrix)
- `alignment_matrix_gemini.npy` (768x384 mapping matrix)

### 2. Configure Environment

Update `.env` file:

```bash
# Default embedder type for queries
QUERY_EMBEDDER_TYPE=ollama

# Calibration matrix paths
EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI=alignment_matrix_gemini.npy
EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA=alignment_matrix_ollama.npy

# Gemini API key (required for Gemini embeddings)
GEMINI_API_KEY=your-api-key-here
GEMINI_EMBEDDING_MODEL=models/embedding-001

# Ollama configuration
OLLAMA_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

## Usage

### Web UI

1. Start the backend:
   ```bash
   ./venv/bin/python src/api_server.py
   ```

2. Start the web UI:
   ```bash
   cd web-ui
   npm run dev
   ```

3. In the query form, select embedder from dropdown:
   - **Auto (server default)**: Uses `QUERY_EMBEDDER_TYPE` from `.env`
   - **Ollama**: Uses local Ollama embeddings (free, fast)
   - **Gemini**: Uses Google Gemini embeddings (premium, higher quality)

### API

Send POST request to `/query` endpoint:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 5,
    "use_cache": true,
    "query_embedder_type": "gemini"
  }'
```

Parameters:
- `query_embedder_type`: `"ollama"` or `"gemini"` (optional, uses server default if omitted)

### Python SDK

```python
from src.document_store.orchestrator import SemanticPatternOrchestrator

orchestrator = SemanticPatternOrchestrator()

# Use Gemini embeddings
result = orchestrator.query(
    query="What is RAPTOR RAG?",
    top_k=5,
    query_embedder_type="gemini"
)

# Use Ollama embeddings
result = orchestrator.query(
    query="What is RAPTOR RAG?",
    top_k=5,
    query_embedder_type="ollama"
)

# Use default embedder (from QUERY_EMBEDDER_TYPE)
result = orchestrator.query(
    query="What is RAPTOR RAG?",
    top_k=5
)
```

## Embedder Comparison

| Feature | Ollama (nomic-embed-text) | Gemini (embedding-001) |
|---------|---------------------------|------------------------|
| **Cost** | Free (local) | Pay per API call |
| **Speed** | Fast (local inference) | Network latency |
| **Quality** | Good for general queries | Better semantic understanding |
| **Availability** | Requires Ollama running | Requires API key + internet |
| **Dimension** | 768 | 768 |
| **Use Case** | Development, cost-sensitive | Production, quality-critical |

## Testing

Run the test script to verify embedder selection:

```bash
./venv/bin/python scripts/test_embedder_selection.py
```

Expected output:
```
✅ ollama: Matrix loaded, shape (768, 384)
✅ gemini: Matrix loaded, shape (768, 384)
✅ Ollama embedding successful
✅ Gemini embedding successful
✅ All tests completed!
```

## Troubleshooting

### Warning: Calibration matrix not available

**Symptom**:
```
WARNING:...:Calibration matrix not available for gemini. Falling back to local model.
```

**Solution**:
1. Run calibration script: `./venv/bin/python scripts/calibrate_embeddings.py`
2. Verify matrices exist: `ls -lh alignment_matrix_*.npy`
3. Check `.env` paths are correct

### Gemini API errors

**Symptom**: Gemini embeddings fail with API error

**Solution**:
1. Verify API key is valid in `.env`
2. Check internet connection
3. Verify Gemini API is enabled in Google Cloud Console

### Ollama connection errors

**Symptom**: Ollama embeddings fail with connection error

**Solution**:
1. Verify Ollama is running: `ollama list`
2. Check `OLLAMA_BASE_URL` in `.env` (default: `http://localhost:11434`)
3. Pull embedding model: `ollama pull nomic-embed-text`

## Advanced Configuration

### Custom Embedder Models

Update `.env` to use different models:

```bash
# Use different Ollama model
OLLAMA_MODEL=mxbai-embed-large

# Use different Gemini model
GEMINI_EMBEDDING_MODEL=models/text-embedding-004
```

After changing models, **regenerate calibration matrices**:
```bash
./venv/bin/python scripts/calibrate_embeddings.py
```

### Calibration Sample Texts

Edit `scripts/calibrate_embeddings.py` to customize calibration samples:

```python
SAMPLE_TEXTS = [
    "Your domain-specific text 1",
    "Your domain-specific text 2",
    # ... more samples
]
```

Use texts representative of your domain for best calibration quality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Query Request                        │
│                   (embedder_type: "gemini")                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              HealthcareHybridEmbedder                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Local Model  │  │   Ollama     │  │   Gemini     │      │
│  │  (384 dim)   │  │  (768 dim)   │  │  (768 dim)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         │                  ▼                  ▼              │
│         │          ┌──────────────────────────────┐         │
│         │          │  Calibration Matrices        │         │
│         │          │  ┌────────┐    ┌────────┐   │         │
│         │          │  │ Ollama │    │ Gemini │   │         │
│         │          │  │768→384 │    │768→384 │   │         │
│         │          │  └────────┘    └────────┘   │         │
│         │          └──────────────┬───────────────┘         │
│         │                         │                         │
│         └─────────────────────────┴──────────────┐          │
│                                                   │          │
│                        Unified 384-dim space     │          │
└───────────────────────────────────────────────────┼──────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vector Search (Qdrant)                    │
│              Documents indexed in 384-dim space              │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Development**: Use Ollama (free, fast iteration)
2. **Production**: Consider Gemini for quality-critical queries
3. **Hybrid Approach**: Use Ollama by default, Gemini for complex queries
4. **Caching**: Enable semantic caching to reduce API costs
5. **Monitoring**: Track embedder usage and query quality metrics

## Related Documentation

- [Main README](../README.md)
- [Calibration Script](../scripts/calibrate_embeddings.py)
- [Hybrid Embedder Implementation](../src/document_store/embeddings/hybrid_embedder.py)
- [API Documentation](../src/api_server.py)
