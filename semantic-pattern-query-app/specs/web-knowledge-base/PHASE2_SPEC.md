# Phase 2: Persistent Web Knowledge Base

## Overview

Implement a persistent vector store for web search results to enable:
1. **Caching**: Avoid repeated web fetches for same content
2. **Audit Trail**: Full provenance tracking for compliance
3. **Citations**: Proper attribution for all web-sourced information
4. **Continuous Learning**: Reinforcement learning from usage patterns
5. **Explainability**: Transparent source tracking

## Architecture

### 3-Tier Retrieval System

```
┌─────────────────────────────────────────────────────────────┐
│ User Query: "What are the latest RAG patterns in 2025?"    │
└─────────────────────────────────────────────────────────────┘
                            ↓
    ╔═══════════════════════════════════════════════════════╗
    ║         RETRIEVAL LAYERS (Weighted RRF Fusion)        ║
    ╠═══════════════════════════════════════════════════════╣
    ║                                                         ║
    ║ 🏠 TIER 1: Pattern Library (Weight 1.0)               ║
    ║    ├─ Qdrant Collection: "patterns"                   ║
    ║    ├─ Elasticsearch Index: "patterns_bm25"            ║
    ║    └─ Source: Curated, trusted patterns               ║
    ║                                                         ║
    ║ 📚 TIER 2: Web Knowledge Base (Weight 0.9) ⭐ NEW     ║
    ║    ├─ Qdrant Collection: "web_knowledge"              ║
    ║    ├─ Source: Previously fetched web articles         ║
    ║    ├─ Features: Deduplication, freshness, audit       ║
    ║    └─ TTL: Configurable expiry (default 30 days)      ║
    ║                                                         ║
    ║ 🌐 TIER 3: Live Web Search (Weight 0.7)               ║
    ║    ├─ Trafilatura + DuckDuckGo (Phase 1)              ║
    ║    ├─ Only triggered if Tier 1+2 insufficient         ║
    ║    └─ New results → AUTO-STORED in Tier 2             ║
    ║                                                         ║
    ╚═══════════════════════════════════════════════════════╝
                            ↓
                    Weighted RRF Fusion
                            ↓
                    LLM with Citations
```

## Database Schema

### Qdrant Collection: `web_knowledge`

```python
{
    "id": "uuid-v4",
    "vector": [0.1, 0.2, ...],  # 768-dim embedding

    # Core content
    "payload": {
        "content": "Full article text (from Trafilatura)",
        "content_hash": "sha256-hash",  # For deduplication

        # Source metadata (AUDIT TRAIL)
        "url": "https://anthropic.com/contextual-retrieval",
        "domain": "anthropic.com",
        "title": "Introducing Contextual Retrieval",
        "author": "Anthropic Team",
        "content_date": "2024-09-19",  # When article was published

        # Extraction metadata
        "extraction_method": "trafilatura",
        "fetched_timestamp": "2025-01-19T10:30:00Z",
        "character_count": 2000,
        "has_structured_data": true,

        # Trust & quality
        "trust_score": 0.9,
        "domain_type": "trusted",  # trusted | default | blocked

        # Freshness management
        "expiry_date": "2025-02-19T10:30:00Z",  # TTL
        "is_expired": false,
        "refresh_count": 0,

        # Usage analytics (REINFORCEMENT LEARNING)
        "query_triggered_by": "latest RAG patterns 2024",
        "times_retrieved": 5,
        "last_retrieved": "2025-01-19T14:00:00Z",
        "user_feedback_score": 0.8,  # Future: user ratings
        "citation_count": 3,  # How many times cited

        # Citation format
        "citation_text": "Anthropic (2024). Introducing Contextual Retrieval. Retrieved from https://anthropic.com/contextual-retrieval",

        # Audit & compliance
        "is_verified": true,
        "verification_date": "2025-01-19T10:30:00Z",
        "audit_trail": [
            {"action": "created", "timestamp": "2025-01-19T10:30:00Z"},
            {"action": "accessed", "timestamp": "2025-01-19T14:00:00Z", "query": "..."}
        ]
    }
}
```

## Implementation Phases

### Phase 2.1: Core Infrastructure ✅ NEXT
- [ ] Create Qdrant collection `web_knowledge`
- [ ] Implement `WebKnowledgeBaseManager` class
- [ ] Add configuration for TTL, max size, freshness
- [ ] Update `.env.example` with new settings

### Phase 2.2: Ingestion Pipeline
- [ ] Auto-ingest web search results to Web KB
- [ ] Deduplication by URL and content hash
- [ ] Metadata extraction and enrichment
- [ ] Update existing results (refresh timestamps)

### Phase 2.3: Retrieval Integration
- [ ] Add Web KB search to orchestrator
- [ ] Implement 3-tier weighted RRF fusion
- [ ] Freshness checking and filtering
- [ ] Fallback logic: KB → Live Web

### Phase 2.4: Citation System
- [ ] Citation metadata in search results
- [ ] Format citations (APA, MLA, Chicago)
- [ ] Include citations in LLM responses
- [ ] API endpoint for citation retrieval

### Phase 2.5: Maintenance & Analytics
- [ ] Expiry cleanup job (cron/scheduler)
- [ ] Usage analytics tracking
- [ ] Refresh stale content
- [ ] Export audit trail

### Phase 2.6: Testing
- [ ] Unit tests for WebKnowledgeBaseManager
- [ ] Integration tests for 3-tier retrieval
- [ ] Citation format tests
- [ ] Audit trail verification tests

## Configuration

### Environment Variables

```bash
# Web Knowledge Base Settings
ENABLE_WEB_KNOWLEDGE_BASE=true
WEB_KB_COLLECTION_NAME=web_knowledge
WEB_KB_TTL_DAYS=30
WEB_KB_MAX_SIZE=10000  # Max documents
WEB_KB_ENABLE_AUTO_INGEST=true
WEB_KB_ENABLE_AUTO_REFRESH=true
WEB_KB_REFRESH_THRESHOLD_DAYS=7

# Tier Weights
TIER_PATTERN_LIBRARY_WEIGHT=1.0
TIER_WEB_KB_WEIGHT=0.9
TIER_LIVE_WEB_WEIGHT=0.7
```

## API Changes

### Query Response with Citations

```json
{
  "answer": "Contextual Retrieval improves RAG accuracy by 49% [1]. It works by adding context to chunks before embedding [2]...",

  "citations": [
    {
      "id": 1,
      "title": "Introducing Contextual Retrieval",
      "authors": ["Anthropic Team"],
      "url": "https://anthropic.com/contextual-retrieval",
      "publication_date": "2024-09-19",
      "access_date": "2025-01-19",
      "source_type": "web_knowledge_base",
      "trust_score": 0.9,
      "citation_apa": "Anthropic Team (2024, September 19). Introducing Contextual Retrieval. Anthropic. https://anthropic.com/contextual-retrieval"
    },
    {
      "id": 2,
      "title": "Basic RAG Pattern",
      "source_type": "pattern_library",
      "trust_score": 1.0
    }
  ],

  "sources": [
    {
      "content": "...",
      "metadata": {
        "layer": "web_knowledge_base",
        "fetched_date": "2025-01-12",
        "times_accessed": 5
      }
    }
  ],

  "retrieval_stats": {
    "tier_1_results": 2,
    "tier_2_results": 3,
    "tier_3_results": 0,  // No live web needed!
    "cache_hit": true
  }
}
```

## Benefits

### 1. Performance ⚡
- **10-100x faster** for repeated queries
- No web latency for cached content
- Reduced API rate limiting issues

### 2. Cost Savings 💰
- Fewer web API calls
- Bandwidth savings
- Reduced Trafilatura extraction costs

### 3. Compliance 📋
- Full audit trail for every source
- Provenance tracking
- Regulatory compliance ready

### 4. Quality 🎯
- Usage-based quality signals
- Continuous learning from feedback
- Stale content detection

### 5. User Experience ✨
- Proper citations
- Transparent sourcing
- Explainable AI

## Success Metrics

- **Cache Hit Rate**: % of queries satisfied by Web KB (target: 60%+)
- **Latency Reduction**: Average query time improvement (target: 50%+)
- **Citation Coverage**: % of answers with citations (target: 100%)
- **Audit Compliance**: 100% of web sources traceable

## Implementation Timeline

- **Phase 2.1**: 2 hours (Core infrastructure)
- **Phase 2.2**: 2 hours (Ingestion)
- **Phase 2.3**: 3 hours (Retrieval integration)
- **Phase 2.4**: 2 hours (Citations)
- **Phase 2.5**: 1 hour (Maintenance)
- **Phase 2.6**: 2 hours (Testing)

**Total**: ~12 hours

## Next Steps

1. Create `WebKnowledgeBaseManager` class
2. Set up Qdrant collection
3. Implement auto-ingestion on web search
4. Add 3-tier retrieval to orchestrator
5. Build citation system
6. Add comprehensive tests
