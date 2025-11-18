# Standardized Port Configuration

This document defines all ports used by the RAG system to prevent conflicts.

## Port Assignments

| Service | Port | Description | Configuration |
|---------|------|-------------|---------------|
| **API Server** | `8000` | FastAPI backend with metrics endpoint | `API_PORT` env var or `.ports` file |
| **Web UI** | `5173` | Vite dev server (frontend) | Vite default (auto-increments if port in use) |
| **Grafana** | `3333` | Monitoring dashboards | `docker-compose.yml` |
| **Prometheus** | `9090` | Metrics collection | `docker-compose.yml` |
| **Elasticsearch** | `9200` | BM25 search engine | `docker-compose.yml` |
| **Elasticsearch** | `9300` | Elasticsearch cluster communication | `docker-compose.yml` |
| **Qdrant** | `6333` | Vector database API | `docker-compose.yml` |
| **Qdrant** | `6334` | Qdrant gRPC interface | `docker-compose.yml` |
| **Redis** | `6380` | Cache (mapped from internal 6379) | `docker-compose.yml` |

## Port Configuration File

Ports are defined in `.ports` file:

```bash
# Load ports
source .ports
export API_PORT=${API_PORT:-8000}
```

## Starting Services

### API Server
```bash
# Option 1: Use start script
./scripts/start-server.sh

# Option 2: Manual start
source .ports
export API_PORT=${API_PORT:-8000}
source venv/bin/activate
python src/api_server.py

# Option 3: Stop server
./scripts/stop-server.sh
```

### Docker Services (Elasticsearch, Qdrant, Redis, Prometheus, Grafana)
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d elasticsearch qdrant redis prometheus grafana
```

### Web UI
```bash
cd web-ui
npm run dev  # Uses port 5173 (Vite default)
```

## Port Conflict Resolution

If a port is already in use:

1. **Check what's using the port:**
   ```bash
   lsof -ti:8000
   ```

2. **Kill the process (if needed):**
   ```bash
   kill $(lsof -ti:8000)
   ```

3. **Or change the port in `.ports` file:**
   ```bash
   API_PORT=8001  # Use different port
   ```

## Changing Ports

To change a port:

1. **API Server:** Update `API_PORT` in `.ports` or set environment variable
2. **Grafana:** Update `docker-compose.yml` (port mapping, currently `3333:3000`)
3. **Prometheus:** Update `docker-compose.yml` (port mapping, currently `9090:9090`)
4. **Elasticsearch:** Update `docker-compose.yml` (port mappings)
5. **Qdrant:** Update `docker-compose.yml` (port mappings)
6. **Redis:** Update `docker-compose.yml` (port mapping, currently `6380:6379`)
7. **Web UI:** Update `vite.config.js` or use `--port` flag

## Verification

Check all services are running:

```bash
# Check all Docker containers
docker ps

# API Server
curl http://localhost:8000/
curl http://localhost:8000/metrics

# Grafana
curl http://localhost:3333/api/health

# Prometheus
curl http://localhost:9090/-/healthy

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Qdrant
curl http://localhost:6333/healthz

# Redis
redis-cli -p 6380 ping
```

## Quick Links

- **Web UI**: http://localhost:5173
- **API Server**: http://localhost:8000
- **API Metrics**: http://localhost:8000/metrics
- **Grafana Dashboards**: http://localhost:3333 (admin/admin)
- **Prometheus UI**: http://localhost:9090
- **Elasticsearch**: http://localhost:9200
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Notes

- Port 5173 is the Vite default (will auto-increment to 5174, 5175, etc. if port is in use)
- Port 3333 is used for Grafana (changed from default 3000 to avoid SSH tunnel conflicts)
- Port 8000 is the default API port (configurable via `API_PORT`)
- Port 6380 is used for Redis (mapped from internal 6379 to avoid conflicts)
- All infrastructure services run in Docker containers (see `docker-compose.yml`)
- For dashboard setup and access, see [guides/GRAFANA_QUALITY_DASHBOARDS.md](guides/GRAFANA_QUALITY_DASHBOARDS.md)

