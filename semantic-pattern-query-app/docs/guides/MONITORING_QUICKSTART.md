# Monitoring Quick Start

## 🚀 Services Status

### ✅ Prometheus
- **URL**: http://localhost:9090
- **Status**: Running
- **Scraping**: Every 15 seconds from `host.docker.internal:8000/metrics`

### ✅ Grafana  
- **URL**: http://localhost:3005
- **Username**: `admin`
- **Password**: `admin`
- **Status**: Running

## 📊 Quick Access

1. **Grafana Dashboard**: http://localhost:3005
   - Login: admin/admin
   - Go to Dashboards → New Dashboard

2. **Prometheus UI**: http://localhost:9090
   - Check targets: Status → Targets
   - Query metrics: Graph tab

## 🔍 Verify Setup

### Check if API Server is Running
```bash
curl http://localhost:8000/
# Should return: {"name":"Semantic Pattern Query API",...}
```

### Check Metrics Endpoint
```bash
curl http://localhost:8000/metrics
# Should return Prometheus metrics
```

### Check Prometheus Targets
1. Open http://localhost:9090
2. Go to **Status → Targets**
3. Look for `rag-api` - should show **UP** (green)

### Test a Query to Generate Metrics
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How does contextual retrieval work?"}'
```

Then check metrics:
```bash
curl http://localhost:8000/metrics | grep rag_queries_total
```

## 📈 Create Your First Dashboard

1. **Login to Grafana**: http://localhost:3005 (admin/admin)

2. **Add Data Source** (if not auto-configured):
   - Configuration → Data Sources
   - Add Prometheus
   - URL: `http://prometheus:9090`
   - Save & Test

3. **Create Dashboard**:
   - Dashboards → New Dashboard
   - Add Panel
   - Use Prometheus query: `rate(rag_queries_total[5m])`
   - Save

## 🛠️ Management

### Start Monitoring
```bash
cd semantic-pattern-query-app
docker-compose -f docker-compose.monitoring.yml up -d
```

### Stop Monitoring
```bash
docker-compose -f docker-compose.monitoring.yml down
```

### View Logs
```bash
docker logs rag-prometheus
docker logs rag-grafana
```

## 📝 Next Steps

See `docs/MONITORING_SETUP.md` for detailed guide and troubleshooting.

