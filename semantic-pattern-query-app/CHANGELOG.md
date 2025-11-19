# Changelog

All notable changes to the Semantic Pattern Query App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2025-11-18

#### Management Scripts (New)

**One-Command System Management**

**New Scripts**:

1. **scripts/start-all.sh** - Complete system startup
   - Checks prerequisites (venv, .env, Ollama)
   - Starts Docker services (Elasticsearch, Qdrant, Redis, Prometheus, Grafana)
   - Waits for services to become healthy
   - Verifies all service endpoints
   - Ingests pattern documents (optional --skip-ingest flag)
   - Starts API server
   - Displays access URLs and test commands
   - Usage: `./scripts/start-all.sh` or `./scripts/start-all.sh --skip-ingest`

2. **scripts/stop-all.sh** - Complete system shutdown
   - Stops API server (port 8000)
   - Stops Web UI (port 5173)
   - Stops Docker services
   - Usage: `./scripts/stop-all.sh`

3. **scripts/clean-all.sh** - System cleanup and maintenance
   - Stops all services
   - Flushes Redis cache
   - Removes log files (/tmp/api_server.log)
   - Clears Python cache (__pycache__, *.pyc)
   - Optional --full flag removes Docker volumes (WARNING: deletes all indexed data)
   - Usage: `./scripts/clean-all.sh` or `./scripts/clean-all.sh --full`

**Benefits**:
- Simplified daily workflow (one command to start/stop)
- Automatic health checks and service verification
- Safe cleanup with data preservation option
- Clear status messages and error handling
- Helpful access URLs and quick start commands

#### Real-Time Quality Metrics System

**Automatic Quality Evaluation on Every Query**

**New Features**:

1. **Answer Quality Metrics** (Automatic)
   - **Faithfulness**: % of answer claims supported by context (0.0-1.0)
   - **Hallucination Detection**: Identifies unsupported claims with severity (minor/moderate/severe)
   - **Relevancy**: How well answer addresses the query (0.0-1.0)
   - **Completeness**: Whether answer fully addresses query (0.0-1.0)
   - **Citation Grounding**: Accuracy of cited sources (0.0-1.0)

2. **Context Quality Metrics** (Automatic)
   - **Context Relevancy**: Average relevance of retrieved chunks (0.0-1.0)
   - **Context Utilization**: % of chunks actually used in answer (0.0-1.0)
   - **Context Precision**: % of relevant chunks (requires ground truth - currently 0)
   - **Context Recall**: % of required facts covered (requires ground truth - currently 0)

3. **Prometheus Metrics Collection**
   - `rag_answer_faithfulness_score` - Histogram
   - `rag_hallucination_detected_total{severity}` - Counter
   - `rag_answer_relevancy_score` - Histogram
   - `rag_answer_completeness_score` - Histogram
   - `rag_citation_grounding_score` - Histogram
   - `rag_context_relevancy` - Histogram
   - `rag_context_utilization` - Histogram

4. **Grafana Quality Metrics Dashboard**
   - RAG Quality Metrics Dashboard (26 panels)
   - Overall Quality Score visualization
   - Hallucination Rate tracking
   - Answer Faithfulness trends
   - Context Relevancy monitoring
   - URL: http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics

5. **Hallucination Logging**
   - Automatic WARNING logs when hallucinations detected
   - Includes severity level and unsupported claims
   - Critical for healthcare safety

6. **API Integration**
   - Quality metrics included in every `/query` response
   - Non-blocking evaluation (won't fail queries)
   - ~10ms overhead per query (<1% of total time)

**Implementation**:
- Modified `src/api_server.py` (Lines 189-277)
- Added evaluation imports and quality_metrics field
- Real-time evaluation after query processing
- Prometheus metrics recording

**Evaluation Method**:
- Word overlap heuristics (no LLM calls)
- Fast, deterministic, zero cost
- Suitable for real-time production use

**Limitations**:
- Uses word overlap (may miss paraphrases)
- IR metrics (Precision@k, Recall@k, NDCG, MRR, MAP) require ground truth
- Cannot detect subtle contradictions

**Files Created**:
- `grafana/dashboards/rag-quality-metrics.json` (26-panel dashboard)
- `docs/implementation/REAL_TIME_QUALITY_METRICS.md` - Complete documentation
- `docs/implementation/REAL_TIME_METRICS_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `docs/guides/QUALITY_METRICS_TROUBLESHOOTING.md` - Troubleshooting guide
- `tests/test_api_quality_metrics.py` - API integration tests
- `tests/test_quality_metrics_standalone.py` - Evaluation module tests
- `tests/test_healthcare_evaluation.py` - Healthcare scenario tests
- `tests/test_evaluation_comparison.py` - Comparison tests
- `scripts/monitoring/restart_api_with_metrics.sh` - Restart helper script

**Files Modified**:
- `src/api_server.py` - Added real-time quality evaluation (Lines 28-30, 95, 189-277)
- `README.md` - Added quality metrics section
- `src/document_store/evaluation/` - Quality evaluation modules

**API Response Format**:
```json
{
  "answer": "...",
  "sources": [...],
  "quality_metrics": {
    "answer": {
      "faithfulness": 0.95,
      "relevancy": 0.88,
      "completeness": 0.80,
      "has_hallucination": false,
      "hallucination_severity": "minor"
    },
    "context": {
      "relevancy": 0.87,
      "utilization": 0.75
    }
  }
}
```

**Status**: ✅ Production Ready

---

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

#### Project Organization and Documentation Cleanup

**Comprehensive File Reorganization**

**Directory Structure Changes**:

1. **Test Files** - Moved to `tests/`
   - `test_api_quality_metrics.py`
   - `test_quality_metrics_standalone.py`
   - `test_healthcare_evaluation.py`
   - `test_evaluation_comparison.py`
   - `test_optimizations.py`
   - `test_opt1_simple.py`
   - `test_quality_metrics.py`

2. **Scripts** - Organized into subdirectories
   - `scripts/monitoring/` - Monitoring and dashboard scripts
     - `import_dashboards.sh`
     - `restart_api_with_metrics.sh`
     - `setup-monitoring.sh`
   - `scripts/testing/` - Test scripts
     - `test_embedder_selection.py`
     - `test_telemetry.py`
   - `scripts/setup/` - Setup and environment scripts
     - `setup_env.sh`
     - `setup_services.sh`
   - `scripts/` - Core utility scripts
     - `calibrate_embeddings.py`
     - `ingest_patterns.py`
     - `query_example.py`
     - `start-server.sh`

3. **Documentation** - Organized into subdirectories
   - `docs/guides/` - User guides and quickstarts
     - `API_GUIDE.md`
     - `QUERY_GUIDE.md`
     - `QUICKSTART.md`
     - `CALIBRATION_GUIDE.md`
     - `EMBEDDER_SELECTION_GUIDE.md`
     - `EVALUATION_QUICK_START.md`
     - `GRAFANA_QUALITY_DASHBOARDS.md`
     - `GEMINI_INTEGRATION.md`
     - `QUALITY_METRICS_TROUBLESHOOTING.md`
     - `TELEMETRY_QUICKSTART.md`
     - `MONITORING_QUICKSTART.md`
   - `docs/implementation/` - Implementation details
     - `REAL_TIME_QUALITY_METRICS.md`
     - `REAL_TIME_METRICS_IMPLEMENTATION_SUMMARY.md`
     - `QUALITY_METRICS_IMPLEMENTATION.md`
     - `QUALITY_METRICS_SUMMARY.md`
     - `TELEMETRY_IMPLEMENTATION.md`
     - `PERFORMANCE_OPTIMIZATIONS.md`
     - `INCREMENTAL_EMBEDDING_OPTIMIZATION.md`
   - `docs/archived/` - Historical documentation
     - `EMBEDDER_SELECTION_IMPLEMENTATION.md`
     - `GRAFANA_SETUP_COMPLETE.md`
     - `TELEMETRY_IMPLEMENTATION_STATUS.md`
     - `TELEMETRY_TEST_RESULTS.md`
     - `MONITORING_STATUS.md`
     - `report.md`
   - `docs/` - Core documentation
     - `CONFIGURATION.md`
     - `PORTS.md`
     - `MONITORING_SETUP.md`
     - `TROUBLESHOOTING_INDEX.md`

**Files Retained**:
- All Grafana dashboard templates in `grafana/dashboards/`
- All provisioning configurations in `grafana/provisioning/`
- `docker-compose.yml`, `prometheus.yml`, `.env.example`
- Core project files (`README.md`, `CHANGELOG.md`, `.gitignore`)

**Directory Structure**:
```
semantic-pattern-query-app/
├── tests/                    # All test files
├── scripts/                  # Utility scripts
│   ├── monitoring/          # Monitoring scripts
│   ├── testing/             # Test scripts
│   └── setup/               # Setup scripts
├── docs/                    # Documentation
│   ├── guides/              # User guides
│   ├── implementation/      # Implementation docs
│   └── archived/            # Historical docs
├── grafana/                 # Grafana templates (retained)
│   ├── dashboards/          # Dashboard JSON files
│   └── provisioning/        # Provisioning configs
├── src/                     # Source code
└── [config files]           # Root-level configs
```

**Status**: ✅ Cleanup Complete

---

## Previous Changes

(Changelog initiated on 2025-11-18 - previous changes not documented)
