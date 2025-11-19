#!/bin/bash
# Stop all services (API server + Docker infrastructure)

echo "🛑 Stopping all services..."
echo ""

# Stop API server
echo "1️⃣  Stopping API Server..."
./scripts/stop-server.sh
echo ""

# Stop Web UI (if running)
echo "2️⃣  Checking for Web UI processes..."
WEB_UI_PIDS=$(lsof -ti:5173 2>/dev/null)
if [ -n "$WEB_UI_PIDS" ]; then
    echo "  Stopping Web UI on port 5173..."
    echo "$WEB_UI_PIDS" | xargs kill -9 2>/dev/null
    echo "  ✅ Web UI stopped"
else
    echo "  No Web UI running on port 5173"
fi
echo ""

# Stop Docker services
echo "3️⃣  Stopping Docker services..."
docker-compose down
echo ""

echo "✅ All services stopped!"
echo ""
echo "Services stopped:"
echo "  - API Server (port 8000)"
echo "  - Web UI (port 5173)"
echo "  - Docker infrastructure (Elasticsearch, Qdrant, Redis, Prometheus, Grafana)"
echo ""
