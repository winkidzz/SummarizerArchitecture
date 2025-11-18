# Telemetry Quick Start Guide

## Installation

Add telemetry dependencies to your `requirements.txt`:

```bash
# Core metrics
prometheus-client>=0.19.0

# Optional: Distributed tracing (for Phase 2)
opentelemetry-api>=1.21.0
opentelemetry-sdk>=1.21.0
opentelemetry-instrumentation-fastapi>=0.42b0
opentelemetry-exporter-jaeger-thrift>=1.21.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Integration (5 minutes)

### Step 1: Add Metrics Endpoint to API Server

In `src/api_server.py`, add:

```python
from prometheus_client import make_asgi_app, generate_latest
from fastapi.responses import Response

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Step 2: Instrument Query Endpoint

In `src/api_server.py`, modify the `query` endpoint:

```python
from src.document_store.monitoring import QueryTelemetry

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the pattern library with telemetry."""
    # Create telemetry tracker
    telemetry = QueryTelemetry(
        query=request.query,
        user_context=request.user_context
    )
    telemetry.start()
    
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.query(
            query=request.query,
            top_k=request.top_k,
            use_cache=request.use_cache,
            user_context=request.user_context,
            query_embedder_type=request.query_embedder_type
        )
        
        # Record final metrics
        telemetry.finish(
            status="success",
            answer=result.get("answer"),
            sources=result.get("sources", [])
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        telemetry.finish(status="error")
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
```

### Step 3: Test Metrics Endpoint

Start your server and check metrics:
```bash
curl http://localhost:8000/metrics
```

You should see Prometheus metrics like:
```
# HELP rag_queries_total Total number of queries processed
# TYPE rag_queries_total counter
rag_queries_total{embedder_type="ollama",status="success",cache_status="miss"} 1.0
```

## Viewing Metrics

### Option 1: Prometheus + Grafana (Recommended)

1. **Install Prometheus:**
```bash
# Download from https://prometheus.io/download/
# Or use Docker:
docker run -d -p 9090:9090 prom/prometheus
```

2. **Configure Prometheus** (`prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'rag-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

3. **Install Grafana:**
```bash
docker run -d -p 3000:3000 grafana/grafana
```

4. **Create Dashboard:**
   - Access Grafana at http://localhost:3000
   - Add Prometheus data source: http://localhost:9090
   - Import dashboard or create custom panels

### Option 2: Simple Metrics Viewer

Use `promtool` to query metrics:
```bash
# Query total queries
curl 'http://localhost:8000/metrics' | grep rag_queries_total

# Query latency
curl 'http://localhost:8000/metrics' | grep rag_query_duration_seconds
```

## Key Metrics to Monitor

### System Health
- `rag_queries_total` - Query volume
- `rag_query_duration_seconds` - Response time
- `rag_errors_total` - Error rate

### Performance
- `rag_retrieval_duration_seconds` - Retrieval speed
- `rag_generation_duration_seconds` - Generation speed
- `rag_embedding_duration_seconds` - Embedding speed

### Quality
- `rag_retrieval_scores` - Retrieval quality
- `rag_cache_hit_rate` - Cache efficiency
- `rag_citation_count` - Answer quality

## Next Steps

1. **Full Integration**: See `TELEMETRY_IMPLEMENTATION.md` for complete integration
2. **Add Tracing**: Implement OpenTelemetry for distributed tracing
3. **Set Up Alerts**: Configure Prometheus alerting rules
4. **Create Dashboards**: Build Grafana dashboards for your team

## Troubleshooting

### Metrics not appearing?
- Check that `/metrics` endpoint is accessible
- Verify Prometheus client is installed
- Check logs for errors

### High overhead?
- Metrics collection is lightweight, but you can:
  - Reduce scrape interval
  - Use sampling for high-volume endpoints
  - Disable debug-level logging

### Need help?
- See `integration_example.py` for code examples
- Check `TELEMETRY_IMPLEMENTATION.md` for detailed guide

