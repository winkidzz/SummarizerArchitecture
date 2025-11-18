# Embedder Selection Implementation Summary

**Date**: November 17, 2024
**Status**: ✅ Complete

## Objective

Enable dynamic embedder selection between Ollama and Gemini, with proper calibration matrices and full UI support.

## What Was Done

### 1. ✅ Generated Calibration Matrices

**Script**: `scripts/calibrate_embeddings.py` (already existed)

**Generated Files**:
- `alignment_matrix_gemini.npy` (2.3MB) - Maps Gemini 768-dim → Local 384-dim
- `alignment_matrix_ollama.npy` (2.3MB) - Maps Ollama 768-dim → Local 384-dim

**Command**:
```bash
./venv/bin/python scripts/calibrate_embeddings.py
```

**Results**:
```
✅ Gemini: (768, 384)
✅ Ollama: (768, 384)
```

### 2. ✅ Updated Configuration Files

**File**: `.env`
- Added `EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI`
- Added `EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA`
- Documented `QUERY_EMBEDDER_TYPE` usage

**File**: `.env.example`
- Updated to match `.env` structure
- Added instructions to run calibration script

### 3. ✅ Verified Existing Implementation

The following components were already properly implemented:

#### Backend API ([src/api_server.py](src/api_server.py))
- ✅ Accepts `query_embedder_type` parameter (line 74)
- ✅ Validates parameter values (lines 154-158)
- ✅ Passes to orchestrator (line 166)

#### Orchestrator ([src/document_store/orchestrator.py](src/document_store/orchestrator.py))
- ✅ Accepts `query_embedder_type` parameter (line 352)
- ✅ Passes to embedder for caching (line 373)
- ✅ Passes to retriever (line 392)

#### Hybrid Embedder ([src/document_store/embeddings/hybrid_embedder.py](src/document_store/embeddings/hybrid_embedder.py))
- ✅ Loads both Ollama and Gemini embedders (lines 74-91)
- ✅ Loads calibration matrices for both (lines 109-113)
- ✅ Dynamic embedder selection in `embed_query()` (lines 149-190)
- ✅ Calibration matrix application (lines 192-234)
- ✅ Re-embedding with selected embedder (lines 236-280)

#### UI ([web-ui/src/components/QueryForm.tsx](web-ui/src/components/QueryForm.tsx))
- ✅ Embedder dropdown with Auto/Ollama/Gemini options (lines 84-96)
- ✅ Sends `query_embedder_type` to API (lines 30-32)

#### API Types ([web-ui/src/lib/api.ts](web-ui/src/lib/api.ts))
- ✅ TypeScript interface includes `query_embedder_type` (line 26)

### 4. ✅ Created Test Script

**File**: `scripts/test_embedder_selection.py`

Tests:
1. ✅ Calibration matrix loading
2. ✅ Ollama query embedding
3. ✅ Gemini query embedding
4. ✅ Default embedder selection

**Test Results**:
```
✅ ollama: Matrix loaded, shape (768, 384)
✅ gemini: Matrix loaded, shape (768, 384)
✅ Ollama embedding successful - Shape: (384,), Norm: 1.0000
✅ Gemini embedding successful - Shape: (384,), Norm: 1.0000
✅ Default embedding successful (using ollama)
```

### 5. ✅ Created Documentation

**File**: `docs/EMBEDDER_SELECTION_GUIDE.md`

Comprehensive guide covering:
- Architecture overview
- Setup instructions
- Usage examples (Web UI, API, Python SDK)
- Embedder comparison table
- Troubleshooting guide
- Advanced configuration
- Architecture diagram
- Best practices

## How It Works

### Architecture Flow

```
User Query → UI Dropdown Selection → API Request
                                          ↓
                            query_embedder_type: "gemini"
                                          ↓
                                    Orchestrator
                                          ↓
                                  HybridEmbedder
                                          ↓
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
                    Gemini API                      Ollama API
                   (768-dim embedding)          (768-dim embedding)
                          ↓                               ↓
                 Calibration Matrix              Calibration Matrix
                   (768 → 384)                     (768 → 384)
                          ↓                               ↓
                          └───────────────┬───────────────┘
                                          ▼
                                  Unified 384-dim space
                                          ↓
                                  Vector Search (Qdrant)
                                  BM25 Search (Elasticsearch)
                                          ↓
                                    Hybrid Retrieval
                                          ↓
                                    RAG Generation
```

### Key Features

1. **Zero Re-indexing**: Documents stay in 384-dim local space
2. **Dynamic Selection**: Switch embedders per query
3. **Calibration**: Premium embeddings mapped to local space
4. **Fallback**: If calibration fails, uses local model
5. **Cost Optimization**: Free local indexing, premium queries

## Testing the Feature

### 1. Unit Tests
```bash
./venv/bin/python scripts/test_embedder_selection.py
```

### 2. Manual Testing via UI

1. Start backend:
   ```bash
   cd /Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app
   ./venv/bin/python src/api_server.py
   ```

2. Start UI:
   ```bash
   cd web-ui
   npm run dev
   ```

3. Test embedder selection:
   - Query: "What is RAPTOR RAG?"
   - Try with: Auto, Ollama, Gemini
   - Verify no calibration warnings in logs

### 3. API Testing
```bash
# Test with Gemini
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "query_embedder_type": "gemini"
  }'

# Test with Ollama
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAPTOR RAG?",
    "query_embedder_type": "ollama"
  }'
```

## Files Modified/Created

### Modified
- `.env` - Added calibration matrix paths
- `.env.example` - Updated with new configuration

### Created
- `alignment_matrix_gemini.npy` - Gemini calibration matrix
- `alignment_matrix_ollama.npy` - Ollama calibration matrix
- `scripts/test_embedder_selection.py` - Test script
- `docs/EMBEDDER_SELECTION_GUIDE.md` - User guide
- `EMBEDDER_SELECTION_IMPLEMENTATION.md` - This summary

### Verified (No Changes Needed)
- `src/api_server.py` - Already supports `query_embedder_type`
- `src/document_store/orchestrator.py` - Already passes parameter
- `src/document_store/embeddings/hybrid_embedder.py` - Fully implemented
- `web-ui/src/components/QueryForm.tsx` - UI already has dropdown
- `web-ui/src/lib/api.ts` - TypeScript types already defined

## Next Steps

### For Users

1. **First Time Setup**:
   ```bash
   # Generate calibration matrices (one-time)
   ./venv/bin/python scripts/calibrate_embeddings.py

   # Verify setup
   ./venv/bin/python scripts/test_embedder_selection.py
   ```

2. **Start Using**:
   - Start backend and UI
   - Select embedder from dropdown
   - Run queries

### For Developers

1. **Regenerate Calibration**: When changing embedding models, run calibration again
2. **Monitor Quality**: Track query quality metrics for each embedder
3. **Cost Analysis**: Monitor Gemini API usage vs quality improvement

## Success Criteria

- [x] Calibration matrices generated for both embedders
- [x] UI dropdown properly sends `query_embedder_type` parameter
- [x] Backend accepts and validates parameter
- [x] Orchestrator passes parameter through retrieval chain
- [x] HybridEmbedder uses correct embedder based on parameter
- [x] No calibration warnings when using either embedder
- [x] Test script passes all tests
- [x] Documentation created

## Troubleshooting Reference

**Issue**: Warning about missing calibration matrix

**Solution**: Run `./venv/bin/python scripts/calibrate_embeddings.py`

---

**Issue**: Gemini API errors

**Solution**: Check `GEMINI_API_KEY` in `.env`

---

**Issue**: Ollama connection errors

**Solution**:
1. Check Ollama is running: `ollama list`
2. Verify model is pulled: `ollama pull nomic-embed-text`

---

## Additional Resources

- [Embedder Selection Guide](docs/EMBEDDER_SELECTION_GUIDE.md)
- [Main README](README.md)
- [Calibration Script](scripts/calibrate_embeddings.py)
- [Test Script](scripts/test_embedder_selection.py)
