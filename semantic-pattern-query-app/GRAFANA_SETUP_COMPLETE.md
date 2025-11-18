# Grafana Dashboard Setup - Complete

**Date**: November 18, 2025
**Status**: ✅ **OPERATIONAL** - All systems running

---

## Quick Access

### Application URLs
- **Web UI**: http://localhost:5173
- **API Server**: http://localhost:8000
- **API Metrics**: http://localhost:8000/metrics

### Monitoring URLs
- **Grafana UI**: http://localhost:3333
  - Username: `admin`
  - Password: `admin`
- **Prometheus UI**: http://localhost:9090
  - Targets: http://localhost:9090/targets

### Infrastructure URLs
- **Elasticsearch**: http://localhost:9200
- **Qdrant**: http://localhost:6333/dashboard
- **Redis**: localhost:6380

---

## Dashboard URLs

All 5 dashboards are now live and accessible:

### 1. RAG System - Real-Time Telemetry
**Best for**: Live monitoring, incident response
- **URL**: http://localhost:3333/d/42498e0c-6a4d-437b-ad44-0908f08b41b8/rag-system-real-time-telemetry
- **Refresh**: 5 seconds
- **Time Range**: Last 15 minutes

### 2. RAG Performance - Detailed Analytics
**Best for**: Performance optimization, bottleneck analysis
- **URL**: http://localhost:3333/d/20bf207c-1df5-46f1-993b-f80e9a8fa718/rag-performance-detailed-analytics
- **Refresh**: 10 seconds
- **Time Range**: Last 30 minutes

### 3. Embedder Comparison - Ollama vs Gemini
**Best for**: Cost optimization, embedder selection
- **URL**: http://localhost:3333/d/15163eb9-36c3-4137-917d-3634a4b0d89b/embedder-comparison-ollama-vs-gemini
- **Refresh**: 30 seconds
- **Time Range**: Last 1 hour

### 4. RAG System Health
**Best for**: Basic health monitoring
- **URL**: http://localhost:3333/d/b0725ff8-29e4-4102-a481-2b89024a5cb5/rag-system-health
- **Refresh**: 10 seconds
- **Time Range**: Default

### 5. Infrastructure Health - System Resources
**Best for**: Infrastructure monitoring, resource planning
- **URL**: http://localhost:3333/d/18220403-0128-4590-9281-d8cc3821157a/infrastructure-health-system-resources
- **Refresh**: 15 seconds
- **Time Range**: Last 15 minutes

---

## System Status

### Docker Containers

All containers running and healthy:

```bash
✅ rag-grafana         - http://localhost:3333 (healthy)
✅ rag-prometheus      - http://localhost:9090 (healthy)
✅ semantic-elasticsearch - http://localhost:9200 (healthy)
✅ semantic-qdrant     - http://localhost:6333 (healthy)
✅ semantic-redis      - http://localhost:6380 (healthy)
```

### Prometheus Targets

```bash
✅ rag-api target: UP (scraping http://host.docker.internal:8000/metrics)
✅ prometheus target: UP (self-monitoring)
```

### Grafana Datasources

```bash
✅ Prometheus datasource configured
   - Name: Prometheus
   - URL: http://prometheus:9090
   - Status: Connected
   - UID: PBFA97CFB590B2093
```

---

## Setup Details

### What Was Configured

#### 1. Docker Compose Services Added

**File**: [docker-compose.yml](docker-compose.yml:52-93)

Added two new services:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Dashboard visualization

**Ports**:
- Prometheus: `9090:9090`
- Grafana: `3333:3000` (external port 3333 due to SSH tunnel on 3000)

**Volumes**:
- Dashboard files: `./grafana/dashboards` → `/var/lib/grafana/dashboards`
- Provisioning configs: `./grafana/provisioning` → `/etc/grafana/provisioning`
- Persistent storage: `grafana_data` and `prometheus_data`

#### 2. Dashboard Import Script

**File**: [scripts/import_dashboards.sh](scripts/import_dashboards.sh)

Automated script that:
- Waits for Grafana to be ready
- Imports all 5 dashboard JSON files via API
- Provides success/failure feedback
- Displays dashboard URLs

**Usage**:
```bash
./scripts/import_dashboards.sh
```

#### 3. Prometheus Configuration

**File**: [prometheus.yml](prometheus.yml)

Configured to scrape:
- RAG API metrics at `host.docker.internal:8000/metrics`
- Self-monitoring at `localhost:9090`

**Scrape interval**: 15 seconds

#### 4. Grafana Provisioning

**Files**:
- [grafana/provisioning/datasources/prometheus.yml](grafana/provisioning/datasources/prometheus.yml)
- [grafana/provisioning/dashboards/dashboards.yml](grafana/provisioning/dashboards/dashboards.yml)

Auto-provisions:
- Prometheus datasource on startup
- Dashboard directory configuration
- Folder structure for dashboard organization

---

## Verification Steps

### 1. Check Container Status

```bash
docker ps | grep -E "(grafana|prometheus)"
```

Expected output:
```
rag-grafana      Up X minutes (healthy)
rag-prometheus   Up X minutes (healthy)
```

### 2. Check Grafana Health

```bash
curl -s http://localhost:3333/api/health | jq
```

Expected output:
```json
{
  "database": "ok",
  "version": "12.2.1",
  "commit": "..."
}
```

### 3. Check Prometheus Targets

```bash
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

Expected output:
```json
{
  "job": "prometheus",
  "health": "up"
}
{
  "job": "rag-api",
  "health": "up"
}
```

### 4. Check Metrics Availability

```bash
curl -s "http://localhost:9090/api/v1/query?query=rag_queries_total" | jq '.data.result | length'
```

Expected output: `1` (or higher if metrics exist)

### 5. Check Dashboards

```bash
curl -s -u admin:admin "http://localhost:3333/api/search?type=dash-db" | jq '.[].title'
```

Expected output:
```
"RAG Performance - Detailed Analytics"
"RAG System - Real-Time Telemetry"
"Embedder Comparison - Ollama vs Gemini"
"RAG System Health"
"Infrastructure Health - System Resources"
```

---

## Usage Examples

### Example 1: Monitor Real-Time Performance

1. Open http://localhost:3333/d/42498e0c-6a4d-437b-ad44-0908f08b41b8/rag-system-real-time-telemetry
2. View live metrics refreshing every 5 seconds
3. Watch query rate, latency, and success rate

### Example 2: Analyze Embedder Performance

1. Open http://localhost:3333/d/15163eb9-36c3-4137-917d-3634a4b0d89b/embedder-comparison-ollama-vs-gemini
2. Compare Ollama vs Gemini latency
3. Analyze cost (free vs paid queries)
4. Evaluate quality metrics

### Example 3: Debug Performance Issues

1. Open http://localhost:3333/d/20bf207c-1df5-46f1-993b-f80e9a8fa718/rag-performance-detailed-analytics
2. Check "Average Latency by Component" panel
3. Identify bottleneck (retrieval vs generation vs embedding)
4. Drill into specific component metrics

### Example 4: Monitor Infrastructure Health

1. Open http://localhost:3333/d/18220403-0128-4590-9281-d8cc3821157a/infrastructure-health-system-resources
2. Check memory and CPU usage
3. Verify component health (Elasticsearch, Qdrant, Redis, Ollama)
4. Monitor request flow

---

## Maintenance

### Restart Services

```bash
# Restart all monitoring services
docker-compose restart prometheus grafana

# Restart specific service
docker-compose restart grafana
```

### Re-import Dashboards

If you make changes to dashboard JSON files:

```bash
./scripts/import_dashboards.sh
```

### View Logs

```bash
# Grafana logs
docker logs rag-grafana

# Prometheus logs
docker logs rag-prometheus

# Follow logs
docker logs -f rag-grafana
```

### Update Dashboard

1. Make changes in Grafana UI
2. Export dashboard JSON (Dashboard Settings → JSON Model)
3. Save to `grafana/dashboards/[name].json`
4. Re-import: `./scripts/import_dashboards.sh`

---

## Troubleshooting

### Issue: Dashboards show "No data"

**Solution**:
1. Check API server is running: `curl http://localhost:8000/metrics`
2. Check Prometheus targets: http://localhost:9090/targets
3. Verify metrics exist: `curl http://localhost:9090/api/v1/query?query=rag_queries_total`
4. Run test query to generate metrics:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "top_k": 5}'
   ```

### Issue: Cannot access Grafana

**Solution**:
1. Check container status: `docker ps | grep grafana`
2. Check logs: `docker logs rag-grafana`
3. Verify port 3333 is free: `lsof -i :3333`
4. Restart: `docker-compose restart grafana`

### Issue: Prometheus not scraping metrics

**Solution**:
1. Check Prometheus config: `cat prometheus.yml`
2. Check targets: http://localhost:9090/targets
3. Verify API server metrics endpoint: `curl http://localhost:8000/metrics`
4. Check Docker network: `docker network inspect semantic-pattern-query-app_default`

### Issue: Datasource connection failed

**Solution**:
1. Check Prometheus is running: `curl http://localhost:9090/-/healthy`
2. Test datasource in Grafana: Settings → Data Sources → Prometheus → Test
3. Check provisioning: `docker logs rag-grafana | grep datasource`
4. Verify datasource URL uses Docker service name: `http://prometheus:9090`

---

## Configuration Files

### Docker Compose

**File**: [docker-compose.yml](docker-compose.yml)

Key sections:
- Lines 52-70: Prometheus service
- Lines 72-93: Grafana service
- Lines 99-100: Data volumes

### Prometheus Config

**File**: [prometheus.yml](prometheus.yml)

Key settings:
- Line 3: Global scrape interval (15s)
- Lines 23-35: RAG API scrape config
- Line 27: Metrics endpoint (`http://host.docker.internal:8000/metrics`)

### Grafana Provisioning

**Datasource**: [grafana/provisioning/datasources/prometheus.yml](grafana/provisioning/datasources/prometheus.yml)
**Dashboards**: [grafana/provisioning/dashboards/dashboards.yml](grafana/provisioning/dashboards/dashboards.yml)

### Dashboard Files

**Directory**: [grafana/dashboards/](grafana/dashboards/)

Files:
- `rag-performance-detailed.json` (457 lines)
- `rag-realtime-dashboard.json` (308 lines)
- `embedder-comparison.json` (348 lines)
- `rag-system-health.json` (75 lines)
- `infrastructure-health.json` (416 lines)

---

## Next Steps

### Recommended Actions

1. **Generate Some Metrics**:
   ```bash
   # Run a few test queries
   for i in {1..10}; do
     curl -X POST http://localhost:8000/query \
       -H "Content-Type: application/json" \
       -d "{\"query\": \"test query $i\", \"top_k\": 5}"
   done
   ```

2. **Explore Dashboards**:
   - Open each dashboard and familiarize yourself
   - Adjust time ranges to see historical data
   - Try different embedder types to compare

3. **Set Up Alerts** (Optional):
   - Create Prometheus alert rules
   - Configure notification channels (Slack, email)
   - Set thresholds for critical metrics

4. **Customize Dashboards**:
   - Adjust panels to your needs
   - Add custom metrics
   - Create team-specific views

---

## Summary

✅ **All systems operational**:
- 5 dashboards imported and accessible
- Prometheus collecting metrics from RAG API
- Grafana connected to Prometheus
- All Docker containers healthy
- Auto-provisioning configured
- Import script ready for updates

**Access Grafana**: http://localhost:3333 (admin/admin)

**View Dashboards**: Navigate to Dashboards → Browse in Grafana UI

---

**Setup Date**: 2025-11-18
**Status**: ✅ COMPLETE
**Version**: 1.0.0
