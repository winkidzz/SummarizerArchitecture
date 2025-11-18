# Embedding Calibration Guide

This guide explains how to calibrate premium embeddings (Gemini/Ollama) to work with the local model space, following the architecture pattern from RAG Architecture.md.

## Overview

The system uses **calibration mapping** to align premium embeddings with the local model space:

- **Documents**: Embedded with local model (`all-MiniLM-L12-v2`, 384 dim) - stored in vector DB
- **Queries**: Embedded with premium model (Gemini 768 dim or Ollama 4096 dim)
- **Calibration**: Maps premium query embeddings → local space (384 dim) for approximate search
- **Re-embedding**: Top candidates re-embedded with premium model for final ranking

## Why Calibration?

Following the architecture pattern:
1. **Better Query Understanding**: Premium embeddings capture query intent better
2. **Cost-Effective**: Only query embeddings use premium models (low volume)
3. **Accurate Search**: Mapped embeddings allow search in local space (fast, free)
4. **Precise Ranking**: Re-embedding with premium model for final accuracy

## Running Calibration

### Prerequisites

1. **Environment Setup**: Ensure `.env` file is configured
   - `GEMINI_API_KEY` (for Gemini calibration)
   - `OLLAMA_MODEL` and `OLLAMA_BASE_URL` (for Ollama calibration)

2. **Dependencies**: All required packages installed
   ```bash
   pip install -r requirements.txt
   ```

### Run Calibration Script

```bash
cd semantic-pattern-query-app
python scripts/calibrate_embeddings.py
```

This will:
- Calibrate Gemini embeddings (if `GEMINI_API_KEY` is set)
- Calibrate Ollama embeddings (if Ollama is running)
- Create separate calibration matrices for each embedder type

### Output Files

The script creates:
- `alignment_matrix_gemini.npy` - Maps Gemini 768 dim → local 384 dim
- `alignment_matrix_ollama.npy` - Maps Ollama 4096 dim → local 384 dim

## How It Works

### Calibration Process

1. **Sample Texts**: Uses 100 representative texts from your domain
2. **Dual Embedding**: Embeds samples with both local and premium models
3. **Matrix Calculation**: Computes alignment matrix using least squares
4. **Save Matrix**: Stores embedder-specific calibration matrix

### Query Flow with Calibration

```
Query → Premium Embedding (Gemini/Ollama)
      → Calibration Mapping (to local space)
      → Approximate Search (in local space)
      → Re-embed Top Candidates (with premium model)
      → Final Ranking
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Embedder-specific calibration matrices
EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI=alignment_matrix_gemini.npy
EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA=alignment_matrix_ollama.npy

# Generic fallback (optional)
EMBEDDING_ALIGNMENT_MATRIX_PATH=alignment_matrix.npy
```

### Custom Sample Texts

Edit `scripts/calibrate_embeddings.py` to customize sample texts:

```python
SAMPLE_TEXTS = [
    "Your domain-specific texts here...",
    # Add more representative texts
] * 5  # Repeat to get more samples
```

## Fallback Behavior

If calibration matrices are not available:
- System falls back to using local model for query embedding
- No calibration needed (backward compatible)
- Approximate search still works, but without premium query understanding

## Verification

### Check Calibration Matrices

```python
import numpy as np

# Check Gemini calibration
gemini_matrix = np.load("alignment_matrix_gemini.npy")
print(f"Gemini matrix shape: {gemini_matrix.shape}")  # Should be (768, 384)

# Check Ollama calibration
ollama_matrix = np.load("alignment_matrix_ollama.npy")
print(f"Ollama matrix shape: {ollama_matrix.shape}")  # Should be (4096, 384)
```

### Test Query Embedding

```python
from src.document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder

# Test with Gemini
embedder = HealthcareHybridEmbedder(query_embedder_type="gemini")
query_emb = embedder.embed_query("test query")
print(f"Query embedding shape: {query_emb.shape}")  # Should be (384,)

# Test with Ollama
embedder = HealthcareHybridEmbedder(query_embedder_type="ollama")
query_emb = embedder.embed_query("test query")
print(f"Query embedding shape: {query_emb.shape}")  # Should be (384,)
```

## Troubleshooting

### "Calibration matrix not available"

**Solution**: Run the calibration script:
```bash
python scripts/calibrate_embeddings.py
```

### "Dimension mismatch" warning

**Expected**: Different embedders have different dimensions:
- Gemini: 768 dim
- Ollama: 4096 dim
- Local: 384 dim

The system handles this automatically using pseudo-inverse.

### Calibration fails for one embedder

**Check**:
1. API key is set (for Gemini)
2. Ollama is running (for Ollama)
3. Network connectivity
4. Model availability

The script will continue with the other embedder if one fails.

## Best Practices

1. **Run Calibration Once**: After initial setup, calibration matrices persist
2. **Use Domain-Specific Texts**: Customize sample texts to match your domain
3. **Re-calibrate When Needed**: If you change models or see quality degradation
4. **Monitor Performance**: Track retrieval quality after calibration
5. **Version Control**: Commit calibration matrices (they're small files)

## Next Steps

After calibration:
1. Test queries with both embedder types
2. Compare retrieval quality (with vs without calibration)
3. Monitor query latency and accuracy
4. Adjust sample texts if needed

## Related Documentation

- [GEMINI_INTEGRATION.md](./GEMINI_INTEGRATION.md) - Gemini integration details
- [RAG Architecture.md](../pattern-query-app/docs/RAG%20Architecture.md) - Architecture reference
- [ENV_SETUP.md](./ENV_SETUP.md) - Environment configuration

