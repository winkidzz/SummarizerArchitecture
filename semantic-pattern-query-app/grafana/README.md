# Grafana Dashboards - RAG System Monitoring

## Overview

Comprehensive Grafana dashboards for monitoring the RAG (Retrieval-Augmented Generation) system in real-time.

## Dashboard Inventory

### 1. **RAG Performance - Detailed Analytics** (`rag-performance-detailed.json`)

**Purpose**: Deep dive into RAG system performance metrics

**Key Metrics**:
- **Query Performance**:
  - Total queries (success vs error)
  - Success rate percentage
  - Query rate (QPS)
  - End-to-end latency (P50, P95, P99)
  - Component-level latency breakdown

- **Retrieval Performance**:
  - Documents retrieved (distribution)
  - Retrieval duration by stage
  - Retriever type distribution

- **Generation & Answer Quality**:
  - Answer length statistics
  - Citation count
  - Generation duration

- **Caching Performance**:
  - Cache hit rate
  - Cache hits vs misses
  - Queries by cache status

**Refresh Rate**: 10s
**Best For**: Performance optimization, identifying bottlenecks

---

### 2. **RAG System - Real-Time Telemetry** (`rag-realtime-dashboard.json`)

**Purpose**: Real-time system monitoring at a glance

**Key Metrics**:
- Total queries counter
- Query rate per second
- Success vs error rate
- Query duration percentiles (P50, P95, P99)
- Retrieval documents and duration
- Generation duration
- Answer length & citations
- Embedding duration
- Cache hit rate gauge

**Refresh Rate**: 5s
**Best For**: Real-time monitoring, incident response

---

### 3. **Embedder Comparison - Ollama vs Gemini** (`embedder-comparison.json`)

**Purpose**: Compare performance between different embedding models

**Key Metrics**:
- **Usage Overview**:
  - Queries by embedder type (pie chart)
  - Query rate by embedder

- **Latency Comparison**:
  - End-to-end latency (P95) comparison
  - Average latency comparison

- **Embedding Performance**:
  - Embedding duration by embedder
  - Duration comparison (bar gauge)

- **Quality Metrics**:
  - Retrieval quality by embedder
  - Success rate by embedder

- **Cost Analysis**:
  - Query volume by embedder (hourly)
  - Embedder selection trend

**Refresh Rate**: 30s
**Best For**: Cost optimization, quality analysis, embedder selection

---

### 4. **RAG System Health** (`rag-system-health.json`)

**Purpose**: Basic system health monitoring

**Key Metrics**:
- Query rate
- Error rate
- Query latency (P50, P95, P99)
- Cache hit rate

**Refresh Rate**: 10s
**Best For**: General health monitoring

---

### 5. **Infrastructure Health - System Resources** (`infrastructure-health.json`)

**Purpose**: Monitor system resources and component health

**Key Metrics**:
- **System Overview**:
  - API server status
  - Total requests
  - Error rate
  - Uptime

- **Python Process Metrics**:
  - Memory usage (resident, virtual)
  - CPU usage
  - Garbage collection
  - Open file descriptors

- **Component Health**:
  - Elasticsearch health
  - Qdrant health
  - Redis health
  - Ollama health

- **Request Flow**:
  - Request rate by status
  - Concurrent requests

**Refresh Rate**: 15s
**Best For**: Infrastructure monitoring, resource planning

---

## Setup & Configuration

### Prerequisites

1. **Prometheus** - Running on `http://prometheus:9090`
2. **Grafana** - Running on `http://localhost:3000`
3. **FastAPI metrics endpoint** - `http://localhost:8000/metrics`

### Directory Structure

```
grafana/
├── dashboards/
│   ├── rag-performance-detailed.json       # NEW
│   ├── rag-realtime-dashboard.json        # Existing
│   ├── embedder-comparison.json           # NEW
│   ├── rag-system-health.json            # Existing
│   └── infrastructure-health.json         # NEW
├── provisioning/
│   ├── dashboards/
│   │   └── dashboards.yml                # Dashboard provisioning config
│   └── datasources/
│       └── prometheus.yml                 # Prometheus datasource config
└── README.md                              # This file
```

### Provisioning Configuration

**File**: `provisioning/dashboards/dashboards.yml`

```yaml
apiVersion: 1

providers:
  - name: 'RAG Dashboards'
    orgId: 1
    folder: 'RAG System'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

**File**: `provisioning/datasources/prometheus.yml`

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
```

---

## Accessing Dashboards

### Via Grafana UI

1. **Open Grafana**: `http://localhost:3333`
2. **Login**: Default credentials (username: `admin`, password: `admin`)
3. **Navigate**: Dashboards → Browse → RAG System folder
4. **Select**: Choose a dashboard from the list

### Direct URLs

- Performance Detailed: `http://localhost:3333/d/rag-performance-detailed`
- Real-Time Telemetry: `http://localhost:3333/d/rag-realtime-dashboard`
- Embedder Comparison: `http://localhost:3333/d/embedder-comparison`
- System Health: `http://localhost:3333/d/rag-system-health`
- Infrastructure Health: `http://localhost:3333/d/infrastructure-health`

**Note**: Grafana runs on port 3333 (not default 3000) to avoid SSH tunnel conflicts.

---

## Metrics Reference

### Available Prometheus Metrics

#### Query Metrics
```
rag_queries_total                      # Total queries (labels: status, cache_status, embedder_type)
rag_query_duration_seconds             # Query duration histogram (labels: embedder_type)
rag_query_tokens                       # Token usage histogram
```

#### Retrieval Metrics
```
rag_retrieval_docs                     # Documents retrieved histogram (labels: retriever_type, stage)
rag_retrieval_duration_seconds         # Retrieval duration histogram (labels: stage)
```

#### Generation Metrics
```
rag_generation_duration_seconds        # Generation duration histogram
rag_answer_length                      # Answer length histogram
rag_citation_count                     # Citation count histogram
```

#### Embedding Metrics
```
rag_embedding_duration_seconds         # Embedding duration histogram (labels: embedder_type)
```

#### Cache Metrics
```
rag_cache_hits_total                   # Cache hits counter
rag_cache_misses_total                 # Cache misses counter
```

#### System Metrics
```
process_cpu_seconds_total              # CPU time
process_resident_memory_bytes          # Memory usage
process_open_fds                       # Open file descriptors
python_gc_collections_total            # Garbage collection
```

---

## Use Cases

### 1. Performance Optimization

**Dashboard**: RAG Performance - Detailed Analytics

**Scenario**: Identifying query latency bottlenecks

**Steps**:
1. Check "End-to-End Latency (P95)" - Is it above target?
2. Compare "Average Latency by Component" - Which is slowest?
3. If **Retrieval** is slow:
   - Check "Documents Retrieved" - Too many?
   - Check "Retrieval Duration by Stage" - Initial vs final?
4. If **Generation** is slow:
   - Check "Generation Duration" - LLM issues?
   - Check "Answer Length" - Generating too much?

---

### 2. Cost Analysis

**Dashboard**: Embedder Comparison - Ollama vs Gemini

**Scenario**: Optimize embedder selection for cost

**Steps**:
1. Check "Queries by Embedder Type" pie chart
2. View "Query Volume by Embedder (Hourly)"
3. Compare "Latency" vs "Quality Metrics"
4. Calculate cost: Gemini queries × $X per 1K embeddings
5. **Decision**: Use Ollama for dev/testing, Gemini for production?

---

### 3. Incident Response

**Dashboard**: RAG System - Real-Time Telemetry

**Scenario**: API is slow or returning errors

**Steps**:
1. Check "Success vs Error Rate" - Spike in errors?
2. Check "Query Duration (P99)" - Latency spike?
3. Switch to "Infrastructure Health" dashboard
4. Check component health (ES, Qdrant, Redis, Ollama)
5. Check memory/CPU usage
6. **Action**: Restart unhealthy component or scale up

---

### 4. Quality Monitoring

**Dashboard**: Embedder Comparison

**Scenario**: Compare retrieval quality between embedders

**Steps**:
1. Run queries with Ollama embedder
2. Run same queries with Gemini embedder
3. Compare "Retrieval Quality by Embedder" - More docs = better?
4. Compare "Success Rate by Embedder"
5. Compare "Answer Length & Citations"
6. **Decision**: Which provides better quality for use case?

---

## Alerting Rules (Prometheus)

### Suggested Alerts

```yaml
# High Error Rate
- alert: HighErrorRate
  expr: 100 * sum(rate(rag_queries_total{status="error"}[5m])) / sum(rate(rag_queries_total[5m])) > 5
  for: 5m
  annotations:
    summary: "High error rate: {{ $value }}%"

# High Latency
- alert: HighLatency
  expr: histogram_quantile(0.95, sum(rate(rag_query_duration_seconds_bucket[1m])) by (le)) > 5
  for: 5m
  annotations:
    summary: "P95 latency above 5s: {{ $value }}s"

# Low Cache Hit Rate
- alert: LowCacheHitRate
  expr: 100 * sum(rate(rag_cache_hits_total[5m])) / (sum(rate(rag_cache_hits_total[5m])) + sum(rate(rag_cache_misses_total[5m]))) < 50
  for: 10m
  annotations:
    summary: "Cache hit rate below 50%: {{ $value }}%"

# Service Down
- alert: ServiceDown
  expr: up{job="fastapi"} == 0
  for: 1m
  annotations:
    summary: "FastAPI service is down"
```

---

## Troubleshooting

### Dashboards Not Showing Up

**Symptom**: Dashboards not visible in Grafana UI

**Solution**:
1. Check dashboard files exist: `ls -la grafana/dashboards/`
2. Check provisioning config: `cat grafana/provisioning/dashboards/dashboards.yml`
3. Restart Grafana: `docker-compose restart grafana`
4. Check Grafana logs: `docker logs grafana`

---

### No Data in Dashboards

**Symptom**: Panels show "No data"

**Solution**:
1. Verify Prometheus is running: `curl http://localhost:9090/-/healthy`
2. Verify metrics endpoint: `curl http://localhost:8000/metrics`
3. Check Prometheus datasource in Grafana: Settings → Data Sources → Prometheus
4. Test query in Grafana Explore: `rag_queries_total`

---

### Metrics Not Updating

**Symptom**: Data is stale, not updating

**Solution**:
1. Check API server is running: `docker ps | grep fastapi`
2. Send test query: `curl -X POST http://localhost:8000/query -d '{"query":"test"}'`
3. Refresh metrics: `curl http://localhost:8000/metrics | grep rag_`
4. Check dashboard refresh rate: Settings → Refresh dropdown

---

## Dashboard Maintenance

### Updating Dashboards

1. **Edit in Grafana UI**:
   - Make changes in Grafana
   - Export JSON (Dashboard Settings → JSON Model)
   - Save to `grafana/dashboards/[name].json`

2. **Edit JSON directly**:
   - Edit `grafana/dashboards/[name].json`
   - Restart Grafana or wait for auto-reload (10s)

### Adding New Metrics

1. **Add metric to code**:
   ```python
   from prometheus_client import Counter
   my_metric = Counter('my_metric_total', 'Description')
   my_metric.inc()
   ```

2. **Verify in Prometheus**:
   - Open `http://localhost:9090`
   - Search for `my_metric_total`

3. **Add to dashboard**:
   - Edit dashboard JSON or use Grafana UI
   - Add panel with query: `my_metric_total`

---

## Best Practices

1. **Dashboard Organization**:
   - Use rows to group related panels
   - Keep most important metrics at the top
   - Use consistent colors across dashboards

2. **Query Performance**:
   - Use appropriate time ranges (shorter = faster)
   - Use recording rules for expensive queries
   - Avoid `count()` without `by()` clause

3. **Visualization**:
   - Use stat panels for single values
   - Use time series for trends
   - Use gauges for percentages/thresholds
   - Use pie charts for distributions

4. **Alerting**:
   - Set realistic thresholds
   - Use `for:` clause to avoid flapping
   - Include context in annotations

---

## Contributing

To add a new dashboard:

1. Create dashboard in Grafana UI
2. Export as JSON
3. Save to `grafana/dashboards/[name].json`
4. Add description to this README
5. Test with clean Grafana instance

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review Grafana logs: `docker logs grafana`
- Review Prometheus logs: `docker logs prometheus`
- Check metrics endpoint: `curl http://localhost:8000/metrics`

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
