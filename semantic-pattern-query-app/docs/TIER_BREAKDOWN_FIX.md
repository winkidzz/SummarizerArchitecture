# Tier Breakdown Display Fix

## Issue
The 3-Tier Retrieval Breakdown component in the web UI was showing tier counts (e.g., "Tier 1: 5 results") but not displaying the actual document content within each tier section.

## Root Cause
Sources returned by the API were missing the `source_type` metadata field needed to identify which tier (Pattern Library, Web KB, or Live Web) each document came from. Without this field, the TierBreakdown component couldn't properly categorize and display documents.

## Fix Applied

### File: `src/document_store/generation/rag_generator.py`

**Lines 246-266**: Updated `_extract_citations()` method to include tier metadata

```python
# Before (missing source_type):
citations.append({
    "doc_index": doc_index,
    "document_id": metadata.get("document_id", ""),
    "source_path": metadata.get("source_path", ""),
    "document_type": metadata.get("document_type", "unknown"),
    "relevance": "cited"
})

# After (includes source_type and score):
metadata = doc.get("metadata", {})
# Extract source_type for tier identification
source_type = metadata.get("source_type") or metadata.get("layer", "pattern_library")

# Get score from any available field
score = doc.get("score") or doc.get("similarity_score") or doc.get("rrf_score")

citation = {
    "doc_index": doc_index,
    "document_id": metadata.get("document_id", ""),
    "source_path": metadata.get("source_path", ""),
    "document_type": metadata.get("document_type", "unknown"),
    "source_type": source_type,  # Add tier metadata
    "relevance": "cited"
}

# Add score if available
if score is not None:
    citation["score"] = score

citations.append(citation)
```

## Changes Made

1. **Added `source_type` field**: Extracted from document metadata with fallback to "pattern_library"
2. **Added `score` field**: Included relevance scores when available for display in UI
3. **Backward compatibility**: Checks both `source_type` (new) and `layer` (old) fields

## Tier Identification Logic

- **Tier 1 (Pattern Library)**: `source_type = "pattern_library"` or missing/null
- **Tier 2 (Web Knowledge Base)**: `source_type = "web_knowledge_base"`
- **Tier 3 (Live Web Search)**: `source_type = "web_search"`

## Testing

Verified with API test:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are RAG patterns?", "top_k": 2}'
```

Response now includes `source_type`:
```json
{
  "sources": [
    {
      "document_id": "basic-rag",
      "source_type": "pattern_library",
      "score": 0.845
    }
  ]
}
```

## Next Steps

The web UI TierBreakdown component should now properly:
1. Group sources by tier based on `source_type` field
2. Display document lists within each tier section
3. Show relevance scores for each document
4. Use color-coded sections (green for Tier 1, blue for Tier 2, purple for Tier 3)

## Server Restart Required

After applying this fix, the API server must be restarted:
```bash
./scripts/stop-server.sh
./scripts/start-server.sh
```

Status: ✅ **Fixed and tested** - sources now include tier metadata for proper UI display.
