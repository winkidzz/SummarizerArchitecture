# Grogu Server Services Summary

**Date**: 2025-11-21  
**User**: winkidzz  
**Server**: grogu

## ✅ Installed Services

### 1. **Elasticsearch 8.19.7**
- **Container**: `semantic-elasticsearch`
- **Ports**: 9200 (HTTP), 9300 (cluster)
- **Status**: ✅ Running (healthy)
- **Storage**: Docker volume `docker-services_elasticsearch_data`
- **Location**: `~/docker-services/`
- **Health**: `http://grogu:9200/_cluster/health`

### 2. **Redis 7.2-alpine**
- **Container**: `semantic-redis`
- **Ports**: 6380 (external) → 6379 (internal)
- **Status**: ✅ Running (healthy)
- **Storage**: Docker volume `docker-services_redis_data`
- **Location**: `~/docker-services/`

### 3. **Qdrant v1.16.0**
- **Container**: `qdrant`
- **Ports**: 6333 (HTTP), 6334 (gRPC)
- **Status**: ✅ Running
- **Storage**: `~/qdrant_storage` (host volume)
- **Health**: `http://grogu:6333/healthz`

### 4. **Prometheus (latest)**
- **Container**: `rag-prometheus`
- **Port**: 9090
- **Status**: ✅ Running
- **Storage**: Docker volume `prometheus_data`
- **Config**: `~/monitoring/prometheus.yml`
- **Health**: `http://grogu:9090/-/healthy`
- **Network**: `monitoring`

### 5. **Grafana (latest)**
- **Container**: `rag-grafana`
- **Port**: 3333 (external) → 3000 (internal)
- **Status**: ✅ Running
- **Storage**: Docker volume `grafana_data`
- **Config**: `~/monitoring/grafana/`
- **Health**: `http://grogu:3333/api/health`
- **Network**: `monitoring`
- **Login**: admin / admin

## 📊 Grafana Dashboards

All dashboards from the project have been copied and are available:

1. **rag-realtime-dashboard.json** - Real-time system monitoring
2. **rag-performance-detailed.json** - Detailed performance analytics
3. **rag-quality-metrics.json** - Quality metrics
4. **rag-system-health.json** - System health overview
5. **infrastructure-health.json** - Infrastructure monitoring
6. **embedder-comparison.json** - Embedder comparison (Ollama vs Gemini)

**Location**: `~/monitoring/grafana/dashboards/`

## 🔧 Configuration Files

### Prometheus
- **Config**: `~/monitoring/prometheus.yml`
- **Scrapes**: 
  - RAG API (host.docker.internal:8000)
  - Prometheus itself (localhost:9090)

### Grafana
- **Dashboards**: `~/monitoring/grafana/dashboards/`
- **Provisioning**: `~/monitoring/grafana/provisioning/`
  - Datasource: `prometheus.yml` (points to `rag-prometheus:9090`)
  - Dashboards: `dashboards.yml`

## 🌐 Access URLs

From other machines, access services at:

- **Elasticsearch**: `http://grogu:9200` or `http://192.168.1.100:9200`
- **Redis**: `grogu:6380` or `192.168.1.100:6380`
- **Qdrant**: `http://grogu:6333` or `http://192.168.1.100:6333`
- **Prometheus**: `http://grogu:9090` or `http://192.168.1.100:9090`
- **Grafana**: `http://grogu:3333` or `http://192.168.1.100:3333`

## 📁 Directory Structure

```
~/docker-services/          # Elasticsearch & Redis docker-compose
  └── docker-compose.yml

~/qdrant_storage/           # Qdrant persistent storage

~/monitoring/               # Prometheus & Grafana configs
  ├── prometheus.yml
  └── grafana/
      ├── dashboards/       # 6 dashboard JSON files
      └── provisioning/
          ├── dashboards/
          │   └── dashboards.yml
          └── datasources/
              └── prometheus.yml
```

## 🛠️ Management Commands

### View All Services
```bash
ssh winkidzz@grogu "docker ps | grep -E '(prometheus|grafana|elasticsearch|redis|qdrant)'"
```

### Elasticsearch & Redis
```bash
# Start/Stop
ssh winkidzz@grogu "cd ~/docker-services && docker-compose up -d"
ssh winkidzz@grogu "cd ~/docker-services && docker-compose down"

# Logs
ssh winkidzz@grogu "cd ~/docker-services && docker-compose logs -f"
```

### Qdrant
```bash
# Start
ssh winkidzz@grogu "docker start qdrant"

# Stop
ssh winkidzz@grogu "docker stop qdrant"

# Logs
ssh winkidzz@grogu "docker logs qdrant -f"
```

### Prometheus
```bash
# Start
ssh winkidzz@grogu "docker start rag-prometheus"

# Stop
ssh winkidzz@grogu "docker stop rag-prometheus"

# Logs
ssh winkidzz@grogu "docker logs rag-prometheus -f"

# Restart (to reload config)
ssh winkidzz@grogu "docker restart rag-prometheus"
```

### Grafana
```bash
# Start
ssh winkidzz@grogu "docker start rag-grafana"

# Stop
ssh winkidzz@grogu "docker stop rag-grafana"

# Logs
ssh winkidzz@grogu "docker logs rag-grafana -f"

# Restart (to reload dashboards/datasources)
ssh winkidzz@grogu "docker restart rag-grafana"
```

## ✅ Verification

### Check All Services
```bash
# Elasticsearch
curl http://grogu:9200/_cluster/health

# Redis
ssh winkidzz@grogu "docker exec semantic-redis redis-cli ping"

# Qdrant
curl http://grogu:6333/healthz

# Prometheus
curl http://grogu:9090/-/healthy

# Grafana
curl http://grogu:3333/api/health
```

## 🔄 Updating Dashboards

To update dashboards:

1. **Edit locally** in `semantic-pattern-query-app/grafana/dashboards/`
2. **Copy to grogu**:
   ```bash
   scp semantic-pattern-query-app/grafana/dashboards/*.json winkidzz@grogu:~/monitoring/grafana/dashboards/
   ```
3. **Restart Grafana** (auto-reloads every 10s, but restart ensures):
   ```bash
   ssh winkidzz@grogu "docker restart rag-grafana"
   ```

## 📝 Notes

- All services use the same versions as the local project
- All dashboards are intact and configured
- Grafana datasource is configured to use `rag-prometheus:9090` via Docker network
- Prometheus is configured to scrape `host.docker.internal:8000` (RAG API on host)
- All persistent data is stored in Docker volumes or host directories

## 🚀 Next Steps

1. **Configure RAG API** to connect to grogu services:
   - `ELASTICSEARCH_URL=http://grogu:9200`
   - `REDIS_HOST=grogu`
   - `REDIS_PORT=6380`
   - `QDRANT_URL=http://grogu:6333`

2. **Update Prometheus config** if RAG API runs on different host/port

3. **Access Grafana** at `http://grogu:3333` and verify dashboards are loaded

