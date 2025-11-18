# Monitoring Setup Status

## ✅ Completed Setup

### 1. Prometheus
- ✅ **Installed and Running**: http://localhost:9090
- ✅ **Configuration**: `prometheus.yml` created
- ✅ **Scraping**: Configured to scrape `host.docker.internal:8000/metrics` every 15 seconds
- ✅ **Status**: Healthy and running

### 2. Grafana
- ✅ **Installed and Running**: http://localhost:3005
- ✅ **Auto-configuration**: Data source and dashboard provisioning configured
- ✅ **Credentials**: admin/admin
- ✅ **Status**: Running

### 3. Configuration Files Created
- ✅ `prometheus.yml` - Prometheus scraping configuration
- ✅ `docker-compose.monitoring.yml` - Docker Compose setup
- ✅ `grafana/provisioning/datasources/prometheus.yml` - Auto-configured data source
- ✅ `grafana/provisioning/dashboards/dashboards.yml` - Dashboard provisioning
- ✅ `setup-monitoring.sh` - Setup script

## ⚠️ Action Required

### Restart API Server

The API server needs to be **restarted** to enable the `/metrics` endpoint:

```bash
# Stop current server (if running)
pkill -f api_server.py

# Start with new metrics endpoint
cd semantic-pattern-query-app
source venv/bin/activate
python src/api_server.py
```

### Verify Metrics Endpoint

After restarting, test the endpoint:
```bash
curl http://localhost:8000/metrics
```

You should see Prometheus metrics like:
```
# HELP rag_queries_total Total number of queries processed
# TYPE rag_queries_total counter
rag_queries_total{embedder_type="ollama",status="success",cache_status="miss"} 0.0
```

## 📊 Access Dashboards

### Grafana
- **URL**: http://localhost:3005
- **Login**: admin / admin
- **Data Source**: Already configured (Prometheus at http://prometheus:9090)

### Prometheus
- **URL**: http://localhost:9090
- **Targets**: Status → Targets (check `rag-api` status)
- **Query**: Graph tab (try `rag_queries_total`)

## 🔧 Troubleshooting

### If Prometheus shows target as DOWN:

1. **Verify API server is running**:
   ```bash
   curl http://localhost:8000/
   ```

2. **Check metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. **If 404, restart API server** (see above)

4. **Check Prometheus can reach the server**:
   - On macOS/Windows: `host.docker.internal` should work
   - If not, update `prometheus.yml` to use your machine's IP

### If Grafana shows no data:

1. **Check data source connection**:
   - Configuration → Data Sources → Prometheus
   - Click "Save & Test"
   - Should show "Data source is working"

2. **Verify Prometheus has metrics**:
   - Open Prometheus: http://localhost:9090
   - Query: `rag_queries_total`
   - Should return data (may be 0 if no queries yet)

3. **Run a test query** to generate metrics:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "test query"}'
   ```

## 📈 Next Steps

1. **Restart API server** (see above)
2. **Verify metrics endpoint** works
3. **Run test queries** to generate metrics
4. **Create Grafana dashboards** with useful queries
5. **Set up alerts** for critical metrics

## 📚 Documentation

- `MONITORING_QUICKSTART.md` - Quick reference
- `MONITORING_SETUP.md` - Detailed setup guide
- `TELEMETRY_QUICKSTART.md` - Telemetry integration guide

