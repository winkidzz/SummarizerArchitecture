# Phase 2 Deployment Guide

## Web Knowledge Base - Persistent Cache with Audit Trail

This guide walks you through deploying Phase 2: Web Knowledge Base with 3-tier retrieval architecture.

---

## ✅ Pre-Deployment Checklist

### 1. Verify Tests Pass

```bash
# Run all Phase 2 tests
./venv/bin/python -m pytest tests/test_web_knowledge_base.py -v

# Expected: 15/15 tests passing ✅

# Run all Phase 1 + Phase 2 tests
./venv/bin/python -m pytest tests/test_web_knowledge_base.py tests/test_trafilatura_provider.py -v

# Expected: 52/52 tests passing ✅
```

### 2. Check Docker Services

Phase 2 requires Qdrant for the Web Knowledge Base:

```bash
# Check if services are running
docker-compose ps

# Should show:
# - qdrant (healthy) - Port 6333
# - elasticsearch (healthy) - Port 9200
# - redis (healthy) - Port 6380
```

If not running:

```bash
docker-compose up -d
```

---

## 📝 Configuration

### Step 1: Update `.env` File

Copy the new configuration from `.env.example`:

```bash
# Web Search (Phase 1 - Already deployed)
ENABLE_WEB_SEARCH=true
WEB_SEARCH_PROVIDER=hybrid  # Trafilatura + DuckDuckGo

# ============================================
# Web Knowledge Base (Phase 2 - NEW)
# ============================================
# Enable persistent web knowledge base for caching and audit
ENABLE_WEB_KNOWLEDGE_BASE=true

# Web KB Collection Settings
WEB_KB_COLLECTION_NAME=web_knowledge  # Qdrant collection name
WEB_KB_TTL_DAYS=30  # Time-to-live for cached web results (days)
WEB_KB_MAX_SIZE=10000  # Maximum documents in Web KB
WEB_KB_ENABLE_AUTO_INGEST=true  # Auto-ingest live web results into KB
WEB_KB_ENABLE_AUTO_REFRESH=true  # Auto-refresh stale content
WEB_KB_REFRESH_THRESHOLD_DAYS=7  # Refresh content older than this

# Tier Weights (for weighted RRF fusion)
TIER_PATTERN_LIBRARY_WEIGHT=1.0  # Tier 1: Curated patterns (highest trust)
TIER_WEB_KB_WEIGHT=0.9  # Tier 2: Cached web results with audit trail
TIER_LIVE_WEB_WEIGHT=0.7  # Tier 3: Live web search (lowest trust)
```

### Step 2: Verify Configuration

```bash
# Check that environment variables are set
grep "ENABLE_WEB_KNOWLEDGE_BASE" .env
grep "WEB_KB_COLLECTION_NAME" .env
grep "TIER_WEB_KB_WEIGHT" .env
```

---

## 🚀 Deployment Steps

### Step 1: Stop Current Services

```bash
# Stop the API server if running
pkill -f "api_server.py"

# Or use the stop script
./scripts/stop-server.sh
```

### Step 2: Initialize Web Knowledge Base Collection

The Web KB collection will be created automatically on first startup. You can verify it after starting the API server:

```bash
# Start the API server
./scripts/start-server.sh

# In another terminal, check Qdrant collections
curl http://localhost:6333/collections

# Should include:
# - healthcare_patterns (existing)
# - web_knowledge (NEW - Phase 2)
```

### Step 3: Test the Deployment

#### Test 1: Basic Query (No Web Search)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "enable_web_search": false
  }'

# Should return normal response without citations
```

#### Test 2: Query with Web Search (First Time)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Contextual Retrieval by Anthropic?",
    "enable_web_search": true,
    "web_mode": "parallel"
  }'

# Expected:
# - Live web search triggered (Tier 3)
# - Results auto-ingested into Web KB
# - Response includes citations
# - retrieval_stats shows tier_3_results > 0
```

#### Test 3: Query with Web Search (Second Time - Cache Hit)

```bash
# Run the same query again
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Contextual Retrieval by Anthropic?",
    "enable_web_search": true,
    "web_mode": "on_low_confidence"
  }'

# Expected:
# - Web KB returns cached results (Tier 2)
# - NO live web search (Tier 3 skipped)
# - Much faster response time
# - Response includes citations from cache
# - retrieval_stats shows tier_2_results > 0, tier_3_results = 0, cache_hit = true
```

#### Test 4: Verify Citations

Check that the response includes citations:

```json
{
  "answer": "...",
  "citations": [
    {
      "id": 1,
      "citation_apa": "Anthropic Team (2024, September 19). Introducing Contextual Retrieval...",
      "source_type": "web_knowledge_base",
      "trust_score": 0.9,
      "url": "https://anthropic.com/contextual-retrieval",
      "title": "Introducing Contextual Retrieval"
    }
  ],
  "retrieval_stats": {
    "tier_1_results": 5,
    "tier_2_results": 3,
    "tier_3_results": 0,
    "cache_hit": true
  }
}
```

---

## 📊 Monitoring

### Check Web KB Statistics

```bash
curl http://localhost:8000/stats

# Should include web_knowledge collection stats
```

### Check Qdrant Web KB Collection

```bash
# Get collection info
curl http://localhost:6333/collections/web_knowledge

# Expected response includes:
# - points_count: Number of cached web results
# - vectors_count: Number of embeddings
# - status: green
```

### Monitor Prometheus Metrics

Visit http://localhost:9090 and query:

```promql
# Web search queries
rag_web_search_queries_total

# Check for "web_kb" mode
rag_web_search_queries_total{mode="web_kb"}

# Web KB cache hit rate
rate(rag_web_search_queries_total{mode="web_kb",status="success"}[5m])
```

### View Grafana Dashboard

Visit http://localhost:3333 (default credentials: admin/admin) and check the RAG Quality Metrics dashboard for web search statistics.

---

## 🧪 Verification Tests

### Test Auto-Ingestion

1. Query with web search enabled (live web triggered)
2. Check Qdrant for new document:

```bash
# Count documents in Web KB
curl http://localhost:6333/collections/web_knowledge | jq '.result.points_count'

# Should increase after web searches
```

### Test Deduplication

1. Run the same web search query twice
2. Check that document count doesn't increase (duplicate detected)

### Test TTL Expiry

Web KB documents expire after 30 days (default). To test:

```bash
# Check expiry dates in documents
curl -X POST http://localhost:6333/collections/web_knowledge/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"limit": 1}' | jq '.result.points[0].payload.expiry_date'
```

### Test Citation Generation

Verify all web results include APA citations:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest RAG techniques 2024",
    "enable_web_search": true
  }' | jq '.citations'
```

---

## 🔧 Troubleshooting

### Issue: Web KB Collection Not Created

**Symptoms**: No `web_knowledge` collection in Qdrant

**Solution**:
```bash
# Check logs
tail -f logs/api_server.log | grep "Web Knowledge Base"

# Should see: "Web Knowledge Base (Tier 2) initialized"

# If not, check environment variable
grep ENABLE_WEB_KNOWLEDGE_BASE .env

# Restart API server
./scripts/stop-server.sh
./scripts/start-server.sh
```

### Issue: Citations Not Appearing in Response

**Symptoms**: Response has no `citations` field

**Solution**:
```bash
# Verify Web KB is enabled
grep ENABLE_WEB_KNOWLEDGE_BASE .env

# Check that web search is enabled in query
# enable_web_search must be true

# Check API server logs for errors
tail -f logs/api_server.log | grep "citation"
```

### Issue: Always Using Live Web (No Cache Hits)

**Symptoms**: `tier_3_results` always > 0, never uses Tier 2

**Solution**:
```bash
# Check that auto-ingest is enabled
grep WEB_KB_ENABLE_AUTO_INGEST .env
# Should be: true

# Check logs for ingestion
tail -f logs/api_server.log | grep "Auto-ingested"

# Verify documents are being stored
curl http://localhost:6333/collections/web_knowledge | jq '.result.points_count'
```

### Issue: Qdrant Connection Error

**Symptoms**: `QdrantClient` connection errors in logs

**Solution**:
```bash
# Verify Qdrant is running
docker-compose ps qdrant

# Check Qdrant health
curl http://localhost:6333/health

# Restart Qdrant if needed
docker-compose restart qdrant
```

---

## 📈 Performance Tuning

### Optimize TTL Settings

Adjust based on content freshness needs:

```bash
# For rapidly changing content (news)
WEB_KB_TTL_DAYS=7

# For stable content (documentation)
WEB_KB_TTL_DAYS=90
```

### Optimize Tier Weights

Adjust RRF fusion weights based on your use case:

```bash
# Trust Web KB more (if high quality cache)
TIER_WEB_KB_WEIGHT=0.95

# Trust local patterns more (if small web KB)
TIER_PATTERN_LIBRARY_WEIGHT=1.0
TIER_WEB_KB_WEIGHT=0.85
```

### Optimize Collection Size

```bash
# Increase for larger knowledge base
WEB_KB_MAX_SIZE=50000

# Decrease for memory constraints
WEB_KB_MAX_SIZE=5000
```

---

## 🔄 Rollback Plan

If you need to rollback to Phase 1 (without Web KB):

### Step 1: Disable Web KB

```bash
# Update .env
ENABLE_WEB_KNOWLEDGE_BASE=false
```

### Step 2: Restart API Server

```bash
./scripts/stop-server.sh
./scripts/start-server.sh
```

### Step 3: (Optional) Remove Web KB Collection

```bash
# Delete collection from Qdrant
curl -X DELETE http://localhost:6333/collections/web_knowledge
```

System will continue to work with 2-tier architecture (Pattern Library + Live Web).

---

## 📚 Additional Resources

- **Phase 2 Spec**: [specs/web-knowledge-base/PHASE2_SPEC.md](specs/web-knowledge-base/PHASE2_SPEC.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Section "Web Knowledge Base v1.2"
- **Web Search Guide**: [docs/guides/WEB_SEARCH_GUIDE.md](docs/guides/WEB_SEARCH_GUIDE.md)
- **README**: [README.md](README.md) - Configuration section

---

## ✅ Deployment Checklist

- [ ] All tests passing (52/52)
- [ ] Docker services running (Qdrant, Elasticsearch, Redis)
- [ ] `.env` configured with Web KB settings
- [ ] API server restarted
- [ ] Web KB collection created in Qdrant
- [ ] Test query with web search (first time - live web)
- [ ] Test query with web search (second time - cache hit)
- [ ] Verify citations in response
- [ ] Verify retrieval stats show correct tiers
- [ ] Monitor Prometheus metrics
- [ ] Check Grafana dashboard

**Deployment Status**: ✅ Ready for Production

---

**Questions?** Check the troubleshooting section or review the full specification in `specs/web-knowledge-base/PHASE2_SPEC.md`.
