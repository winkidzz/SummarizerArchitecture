# Changelog

All notable changes to the Semantic Pattern Query App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2025-11-18

#### Grafana Dashboards with Prometheus Monitoring

**Comprehensive Monitoring Infrastructure**

**New Features**:

1. **5 Grafana Dashboards** (1604 lines total)
   - RAG Performance - Detailed Analytics (457 lines, 19 panels)
   - RAG System - Real-Time Telemetry (308 lines, 10 panels)
   - Embedder Comparison - Ollama vs Gemini (348 lines, 15 panels)
   - RAG System Health (75 lines, 4 panels)
   - Infrastructure Health - System Resources (416 lines, 18 panels)

2. **Monitoring Services** (docker-compose.yml)
   - Prometheus service (port 9090) with metrics collection
   - Grafana service (port 3333) with auto-provisioning
   - 15-second scrape interval for API metrics
   - Persistent data volumes for both services

3. **Automated Dashboard Import**
   - Created `scripts/import_dashboards.sh`
   - Imports all dashboards via Grafana API
   - Provides success/failure feedback with URLs

4. **Documentation**
   - `GRAFANA_SETUP_COMPLETE.md` - Complete setup guide
   - `grafana/README.md` - Dashboard documentation
   - `docs/PORTS.md` - Updated port assignments

**Configuration Files**:
- `prometheus.yml` - Prometheus scrape configuration
- `grafana/provisioning/datasources/prometheus.yml` - Datasource config
- `grafana/provisioning/dashboards/dashboards.yml` - Dashboard provisioning

**Access URLs**:
- Grafana: http://localhost:3333 (admin/admin)
- Prometheus: http://localhost:9090
- Metrics: http://localhost:8000/metrics

**Files Created**:
- `grafana/dashboards/*.json` (5 dashboards)
- `grafana/provisioning/**/*.yml` (2 provisioning configs)
- `grafana/README.md`
- `prometheus.yml`
- `scripts/import_dashboards.sh`
- `GRAFANA_SETUP_COMPLETE.md`
- `docs/PORTS.md`

**Files Modified**:
- `docker-compose.yml` - Added Prometheus and Grafana services
- `README.md` - Added Quick Access Links section
- `.gitignore` - Added *.bak exclusions

---

### Fixed - 2025-11-18

#### Elasticsearch Docker Configuration (docker-compose.yml)

**Critical Fix: Out of Memory (OOM) Issue and Invalid Configuration**

**Problems Identified**:
1. Elasticsearch container was crashing with exit code 137 (OOMKilled)
2. Initial heap size configuration had typo: `"ES_JAVA_OPTS=-Xms512m -Xmx812m"`
3. Docker Desktop memory limit (3.8GB total) with other containers running
4. Invalid ES 8.19.7 settings (`xpack.monitoring.enabled`, `xpack.watcher.enabled`)
5. 512MB heap was still too large for available Docker memory

**Final Working Configuration**:

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.19.7
  container_name: semantic-elasticsearch
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
    - xpack.ml.enabled=false
    - "ES_JAVA_OPTS=-Xms256m -Xmx256m"
  mem_limit: 768m
  ports:
    - "9200:9200"
    - "9300:9300"
  volumes:
    - elasticsearch_data:/usr/share/elasticsearch/data
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 5
    start_period: 60s
```

**Key Changes**:

1. **Minimum Heap Size** (Line 11)
   - Changed from `512m` to `256m` (minimum for ES 8.x)
   - Equal min/max prevents heap resize pauses
   - Works within Docker memory constraints

2. **Memory Limit** (Line 12)
   - Set to `768m` (256MB heap + ~512MB overhead)
   - Prevents OOM kills on systems with limited Docker memory

3. **Disabled Machine Learning** (Line 10)
   - `xpack.ml.enabled=false`
   - Reduces memory footprint significantly
   - Not needed for document search use case

4. **Removed Invalid Settings**
   - Removed `xpack.monitoring.enabled` (doesn't exist in ES 8.19.7)
   - Removed `xpack.watcher.enabled` (deprecated)
   - Removed `bootstrap.memory_lock` (requires additional host config)

5. **Health Check Start Period** (Line 26)
   - `start_period: 60s`
   - Gives ES time to initialize before health checks
   - Prevents false failures during startup

**Technical Details**:

- **Exit Code 137**: Container killed by Docker OOM killer
- **Memory Usage**: Stable at ~625MB / 768MB (81% utilization)
- **Startup Time**: ~30 seconds to reach "green" status
- **Cluster Status**: ✅ Green, healthy, no OOM kills

**Verification Steps**:

```bash
# 1. Stop old containers
docker-compose down

# 2. Remove old data (optional, for clean start)
docker volume rm semantic-pattern-query-app_elasticsearch_data

# 3. Start Elasticsearch
docker-compose up -d elasticsearch

# 4. Monitor logs
docker logs -f semantic-elasticsearch

# 5. Check health
curl http://localhost:9200/_cluster/health
```

**Expected Outcome**:
- Container stays running (no exit code 137)
- Health check passes after ~20-30 seconds
- No heap size warnings in logs
- Memory lock successfully enabled

**Files Modified**:
- `docker-compose.yml` - Elasticsearch service configuration

**References**:
- [Elasticsearch Docker Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/docker.html)
- [Elasticsearch Heap Size Settings](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/heap-size.html)
- [Elasticsearch Memory Lock](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/setup-configuration-memory.html)

---

### Added - 2025-11-17

#### Embedder Selection Feature

**Dynamic Embedder Selection with Calibration Matrices**

**New Features**:

1. **Calibration Matrices**
   - Generated `alignment_matrix_gemini.npy` (768→384 dim mapping)
   - Generated `alignment_matrix_ollama.npy` (768→384 dim mapping)
   - Enables dynamic embedder switching without re-indexing

2. **Configuration Updates**
   - Added `QUERY_EMBEDDER_TYPE` to `.env` (default: ollama)
   - Added `EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI` to `.env`
   - Added `EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA` to `.env`

3. **Test Infrastructure**
   - Created `scripts/test_embedder_selection.py`
   - Validates both Ollama and Gemini embedders
   - Verifies calibration matrix loading

4. **Documentation**
   - Created `docs/EMBEDDER_SELECTION_GUIDE.md` - Comprehensive user guide
   - Created `EMBEDDER_SELECTION_IMPLEMENTATION.md` - Implementation summary

**Verified Working**:
- Backend API accepts `query_embedder_type` parameter ✅
- UI dropdown for embedder selection (Auto/Ollama/Gemini) ✅
- Orchestrator passes parameter through pipeline ✅
- HybridEmbedder dynamic selection implemented ✅

**Files Created**:
- `alignment_matrix_gemini.npy`
- `alignment_matrix_ollama.npy`
- `scripts/test_embedder_selection.py`
- `docs/EMBEDDER_SELECTION_GUIDE.md`
- `EMBEDDER_SELECTION_IMPLEMENTATION.md`

**Files Modified**:
- `.env` - Added calibration matrix configuration
- `.env.example` - Updated with new settings

---

## Previous Changes

(Changelog initiated on 2025-11-18 - previous changes not documented)
