# Gemini Integration for Query Space

This document describes the integration of Google Gemini as an alternative to Ollama for query space embeddings in the RAG pipeline.

## Overview

The system now supports **both Ollama and Gemini** for query space embeddings, configurable via API parameter. This follows the modular design pattern from the reference RAG architecture:

- **Documents**: Always embedded with local model (free, fast bulk indexing)
- **Queries**: Can use either Ollama or Gemini (configurable per query)
- **Re-embedding**: Uses the same premium model chosen for queries

## Architecture

### Layer 3: Hybrid Embedding Strategy

The `HealthcareHybridEmbedder` now supports both embedders:

```python
# Default: Ollama
embedder = HealthcareHybridEmbedder(
    query_embedder_type="ollama",  # or "gemini"
    qwen_model="qwen3:14b",
    gemini_model="models/embedding-001",
    gemini_api_key=os.getenv("GEMINI_API_KEY")
)
```

### Modular Design

- **`qwen_embedder.py`**: Ollama Qwen embedding wrapper
- **`gemini_embedder.py`**: Google Gemini embedding wrapper
- **`hybrid_embedder.py`**: Orchestrates both, selects based on `query_embedder_type`

## Configuration

### Environment Variables

```bash
# For Ollama (default)
OLLAMA_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434

# For Gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_EMBEDDING_MODEL=models/embedding-001  # Optional, defaults to embedding-001
```

### Getting Gemini API Key

1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Set it in your environment: `export GEMINI_API_KEY=your-key`

## API Usage

### Query with Ollama (Default)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 10
  }'
```

### Query with Gemini

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "top_k": 10,
    "query_embedder_type": "gemini"
  }'
```

### Python Example

```python
import requests

# Query with Ollama
response = requests.post("http://localhost:8000/query", json={
    "query": "Explain hybrid retrieval",
    "top_k": 10
})

# Query with Gemini
response = requests.post("http://localhost:8000/query", json={
    "query": "Explain hybrid retrieval",
    "top_k": 10,
    "query_embedder_type": "gemini"
})
```

## Implementation Details

### Embedder Selection

The system creates embedder instances dynamically:

1. **Default**: Orchestrator initializes with Ollama (backward compatible)
2. **Per-Query**: If `query_embedder_type` differs from default, creates temporary embedder
3. **Modular**: Each embedder is independent, no shared state

### Embedding Dimensions

- **Local Model**: 384 dimensions (all-MiniLM-L12-v2)
- **Ollama Qwen**: 4096 dimensions (varies by model)
- **Gemini**: 768 dimensions (embedding-001)

The system handles dimension mismatches automatically through the two-step retrieval process.

### Two-Step Retrieval

1. **Step 1**: Approximate search with local model embeddings (fast, free)
2. **Step 2**: Re-embed top candidates with premium model (Ollama or Gemini) for precision

## Calibration Mapping

The system uses calibration mapping to align premium embeddings (Gemini/Ollama) with the local model space. This follows the architecture pattern from RAG Architecture.md.

### Running Calibration

Calibrate both embedders:

```bash
cd semantic-pattern-query-app
python scripts/calibrate_embeddings.py
```

This creates:
- `alignment_matrix_gemini.npy` (Gemini 768 → local 384)
- `alignment_matrix_ollama.npy` (Ollama 4096 → local 384)

### How It Works

1. **Query Embedding**: Premium model (Gemini/Ollama) embeds the query
2. **Calibration Mapping**: Query embedding mapped to local space (384 dim)
3. **Approximate Search**: Search in local model space (fast, free)
4. **Re-embedding**: Top candidates re-embedded with premium model for final ranking

### Benefits

- ✅ Better query understanding (premium embeddings)
- ✅ Cost-effective (only query embeddings are premium)
- ✅ Accurate approximate search (mapped to local space)
- ✅ Precise final ranking (premium re-embedding)

### Fallback Behavior

If calibration matrices are not available, the system falls back to:
- Using local model for query embedding (no calibration needed)
- This maintains backward compatibility

## Benefits

### Ollama (Default)
- ✅ No API key required
- ✅ Runs locally
- ✅ Free
- ✅ Good for development/testing
- ✅ Supports calibration mapping

### Gemini
- ✅ Higher quality embeddings
- ✅ Consistent API
- ✅ Better for production
- ✅ Cloud-based (requires API key)
- ✅ Supports calibration mapping

## Installation

Install the Gemini dependency:

```bash
cd semantic-pattern-query-app
source venv/bin/activate
pip install google-generativeai>=0.8.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Testing

### Test Gemini Embedder Directly

```python
from src.document_store.embeddings.gemini_embedder import GeminiEmbedder

embedder = GeminiEmbedder()
embedding = embedder.embed_query("test query")
print(f"Embedding dimension: {len(embedding)}")
```

### Test Hybrid Embedder with Gemini

```python
from src.document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder

embedder = HealthcareHybridEmbedder(
    query_embedder_type="gemini",
    gemini_api_key="your-key"
)

# Embed query
query_emb = embedder.embed_query("test")

# Re-embed candidates
candidates = ["doc1", "doc2"]
cand_embs, query_emb_premium = embedder.re_embed_candidates(candidates, "test")
```

## Error Handling

The system gracefully handles errors:

- **Missing API Key**: Raises clear error message
- **API Failure**: Falls back to local model scores
- **Invalid Type**: Returns 400 error with helpful message

## Performance Considerations

- **Ollama**: Local processing, no network latency
- **Gemini**: Network latency (~100-300ms per embedding)
- **Caching**: Both benefit from semantic cache (Layer 7)

## Migration Notes

- **Backward Compatible**: Default behavior unchanged (uses Ollama)
- **No Breaking Changes**: Existing code works without modification
- **Opt-in**: Gemini must be explicitly requested via API parameter

## Future Enhancements

Potential improvements:
- Support for Vertex AI (enterprise Gemini)
- Batch embedding optimization
- Embedding dimension alignment/calibration
- Cost tracking per embedder type

