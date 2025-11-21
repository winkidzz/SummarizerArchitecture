#!/bin/bash
# Start all services in correct sequence
# Usage: ./scripts/start-all.sh [--skip-ingest]
#   --skip-ingest: Skip document ingestion (use if already ingested)

SKIP_INGEST=false
if [ "$1" == "--skip-ingest" ]; then
    SKIP_INGEST=true
fi

echo "🚀 Starting RAG system..."
echo ""

# Check prerequisites
echo "1️⃣  Checking prerequisites..."

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "  ❌ Virtual environment not found"
    echo "  Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
echo "  ✅ Virtual environment found"

# Check .env file
if [ ! -f ".env" ]; then
    echo "  ⚠️  .env file not found (using defaults)"
    echo "  Consider creating .env from .env.example"
else
    echo "  ✅ .env file found"
fi

# Check Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  ⚠️  Ollama not running or not accessible"
    echo "  Make sure Ollama is running: ollama serve"
else
    echo "  ✅ Ollama is running"
fi
echo ""

# Start Docker services
echo "2️⃣  Starting Docker services..."
docker-compose up -d
echo ""

# Wait for services to be healthy
echo "3️⃣  Waiting for services to become healthy (15 seconds)..."
sleep 5
echo "  ⏳ 5 seconds..."
sleep 5
echo "  ⏳ 10 seconds..."
sleep 5
echo "  ✅ Services should be ready"
echo ""

# Verify Docker services
echo "4️⃣  Verifying Docker services..."
SERVICES_OK=true

# Check Elasticsearch
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "  ✅ Elasticsearch (port 9200)"
else
    echo "  ❌ Elasticsearch not responding"
    SERVICES_OK=false
fi

# Check Qdrant
if curl -s http://localhost:6333/healthz > /dev/null 2>&1; then
    echo "  ✅ Qdrant (port 6333)"
else
    echo "  ❌ Qdrant not responding"
    SERVICES_OK=false
fi

# Check Redis
if redis-cli -p 6380 ping > /dev/null 2>&1; then
    echo "  ✅ Redis (port 6380)"
else
    echo "  ⚠️  Redis not responding (may still be starting)"
fi

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "  ✅ Prometheus (port 9090)"
else
    echo "  ⚠️  Prometheus not responding (may still be starting)"
fi

# Check Grafana
if curl -s http://localhost:3333/api/health > /dev/null 2>&1; then
    echo "  ✅ Grafana (port 3333)"
else
    echo "  ⚠️  Grafana not responding (may still be starting)"
fi
echo ""

if [ "$SERVICES_OK" = false ]; then
    echo "  ❌ Some critical services failed to start"
    echo "  Check logs: docker-compose logs"
    exit 1
fi

# Ingest documents (unless skipped)
if [ "$SKIP_INGEST" = false ]; then
    echo "5️⃣  Ingesting pattern documents..."
    source venv/bin/activate
    python scripts/ingest_patterns.py
    if [ $? -ne 0 ]; then
        echo "  ❌ Document ingestion failed"
        exit 1
    fi
    echo "  ✅ Documents ingested"
    echo ""
else
    echo "5️⃣  Skipping document ingestion (--skip-ingest flag)"
    echo ""
fi

# Start API server
echo "6️⃣  Starting API Server..."
./scripts/start-server.sh
if [ $? -ne 0 ]; then
    echo "  ❌ API server failed to start"
    exit 1
fi
echo ""

# Wait for API to be ready
echo "7️⃣  Waiting for API server to be ready..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "  ✅ API server is ready"
        break
    fi
    sleep 1
    echo "  ⏳ Waiting... ($i/10)"
done
echo ""

# Start Web UI
echo "8️⃣  Starting Web UI..."
# Check if node_modules exists
if [ ! -d "web-ui/node_modules" ]; then
    echo "  📦 Installing Web UI dependencies..."
    (cd web-ui && npm install)
fi

# Start Web UI in background
(cd web-ui && nohup npm run dev > ../logs/web-ui.log 2>&1 &)
echo "  ✅ Web UI starting (check logs/web-ui.log for output)"
echo ""

# Wait for Web UI to be ready
echo "9️⃣  Waiting for Web UI to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:5173/ > /dev/null 2>&1; then
        echo "  ✅ Web UI is ready"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo "  ⚠️  Web UI may still be starting (check logs/web-ui.log)"
    else
        echo "  ⏳ Waiting... ($i/15)"
    fi
done
echo ""

# Final status
echo "✅ All services started successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Quick Access Links"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 Web UI:              http://localhost:5173"
echo ""
echo "  🔌 API Server:          http://localhost:8000"
echo "  📖 API Docs:            http://localhost:8000/docs"
echo "  📈 API Metrics:         http://localhost:8000/metrics"
echo ""
echo "  📊 Grafana Dashboards:  http://localhost:3333"
echo "                         (Login: admin/admin)"
echo "  📈 Prometheus:          http://localhost:9090"
echo "  🔍 Elasticsearch:       http://localhost:9200"
echo "  🗂️  Qdrant Dashboard:   http://localhost:6333/dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test the system:"
echo "  curl -X POST http://localhost:8000/query \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"query\": \"What is RAPTOR RAG?\", \"top_k\": 5}'"
echo ""
echo "🛑 Stop all services:"
echo "  ./scripts/stop-all.sh"
echo ""
