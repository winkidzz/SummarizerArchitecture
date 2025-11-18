# Monitoring Setup Guide

## ✅ Services Running

### Prometheus
- **URL**: http://localhost:9090
- **Status**: ✅ Running
- **Scraping**: `host.docker.internal:8000/metrics` (every 15 seconds)

### Grafana
- **URL**: http://localhost:3005
- **Username**: `admin`
- **Password**: `admin`
- **Status**: ✅ Running

## Quick Start

### 1. Access Grafana Dashboard

```bash
# Open in browser
open http://localhost:3005
# Or visit: http://localhost:3005
```

Login credentials:
- Username: `admin`
- Password: `admin`

### 2. Verify Prometheus is Scraping

1. Open Prometheus: http://localhost:9090
2. Go to **Status → Targets**
3. Check that `rag-api` target shows as **UP** (green)
4. If it shows **DOWN**, verify your API server is running on port 8000

### 3. Check Metrics in Prometheus

1. In Prometheus UI, go to **Graph**
2. Try these queries:
   - `rag_queries_total` - Total queries
   - `rate(rag_queries_total[5m])` - Query rate
   - `histogram_quantile(0.95, rag_query_duration_seconds)` - P95 latency

### 4. Create Grafana Dashboard

1. Login to Grafana (http://localhost:3005)
2. Go to **Dashboards → New Dashboard**
3. Add panels with Prometheus queries:

**Query Rate Panel:**
```
rate(rag_queries_total[5m])
```

**Latency Panel (P95):**
```
histogram_quantile(0.95, rag_query_duration_seconds)
```

**Cache Hit Rate:**
```
rate(rag_cache_hits_total[5m]) / (rate(rag_cache_hits_total[5m]) + rate(rag_cache_misses_total[5m]))
```

**Error Rate:**
```
rate(rag_queries_total{status="error"}[5m])
```

## Troubleshooting

### Prometheus Can't Scrape Metrics

**Problem**: Target shows as DOWN in Prometheus

**Solutions**:
1. Verify API server is running:
   ```bash
   curl http://localhost:8000/
   ```

2. Check metrics endpoint directly:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. If using Docker, ensure `host.docker.internal` resolves correctly:
   ```bash
   # On macOS/Windows, this should work
   # On Linux, you may need to use host network mode
   ```

4. Update `prometheus.yml` if needed:
   ```yaml
   # For Linux, try:
   static_configs:
     - targets: ['172.17.0.1:8000']  # Docker bridge IP
   ```

### Grafana Can't Connect to Prometheus

**Problem**: No data in Grafana

**Solutions**:
1. Verify Prometheus is running:
   ```bash
   curl http://localhost:9090/-/healthy
   ```

2. Check Grafana data source:
   - Go to **Configuration → Data Sources**
   - Verify Prometheus URL is: `http://prometheus:9090`
   - Click **Save & Test**

### Port Conflicts

If ports are in use:
- Prometheus (9090): Change in `docker-compose.monitoring.yml`
- Grafana (3005): Change in `docker-compose.monitoring.yml`

## Useful Prometheus Queries

### System Health
```promql
# Query rate
rate(rag_queries_total[5m])

# Error rate
rate(rag_queries_total{status="error"}[5m])

# Success rate
rate(rag_queries_total{status="success"}[5m]) / rate(rag_queries_total[5m])
```

### Performance
```promql
# P50 latency
histogram_quantile(0.50, rag_query_duration_seconds)

# P95 latency
histogram_quantile(0.95, rag_query_duration_seconds)

# P99 latency
histogram_quantile(0.99, rag_query_duration_seconds)
```

### Cache Metrics
```promql
# Cache hit rate
rate(rag_cache_hits_total[5m]) / (rate(rag_cache_hits_total[5m]) + rate(rag_cache_misses_total[5m]))

# Cache operations
rate(rag_cache_operations_total[5m])
```

### Retrieval Metrics
```promql
# Average retrieval duration
rate(rag_retrieval_duration_seconds_sum[5m]) / rate(rag_retrieval_duration_seconds_count[5m])

# Average similarity scores
rate(rag_retrieval_scores_sum[5m]) / rate(rag_retrieval_scores_count[5m])
```

### Generation Metrics
```promql
# Generation duration
rate(rag_generation_duration_seconds_sum[5m]) / rate(rag_generation_duration_seconds_count[5m])

# Token usage
rate(rag_generation_tokens_sum[5m]) / rate(rag_generation_tokens_count[5m])
```

## Management Commands

### Start Services
```bash
cd semantic-pattern-query-app
docker-compose -f docker-compose.monitoring.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.monitoring.yml down
```

### View Logs
```bash
# Prometheus logs
docker logs rag-prometheus

# Grafana logs
docker logs rag-grafana
```

### Restart Services
```bash
docker-compose -f docker-compose.monitoring.yml restart
```

## Next Steps

1. **Create Custom Dashboards**: Build dashboards specific to your needs
2. **Set Up Alerts**: Configure alerting rules in Prometheus
3. **Export Dashboards**: Share dashboard JSON files with your team
4. **Add More Metrics**: Extend telemetry to track additional metrics

## Files Created

- `prometheus.yml` - Prometheus configuration
- `docker-compose.monitoring.yml` - Docker Compose setup
- `grafana/provisioning/` - Grafana auto-configuration
- `setup-monitoring.sh` - Setup script

