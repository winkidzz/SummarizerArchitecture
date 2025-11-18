#!/bin/bash
# Setup script for Prometheus and Grafana monitoring

set -e

echo "🚀 Setting up Prometheus and Grafana for RAG API monitoring..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if API server is running
if ! curl -s http://localhost:8000/metrics > /dev/null 2>&1; then
    echo "⚠️  Warning: API server doesn't appear to be running on port 8000"
    echo "   Please start your API server first:"
    echo "   cd semantic-pattern-query-app && source venv/bin/activate && python src/api_server.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Prometheus and Grafana
echo "📦 Starting Prometheus and Grafana containers..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Check if Prometheus is accessible
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is running at http://localhost:9090"
else
    echo "⚠️  Prometheus may not be fully ready yet. Check http://localhost:9090"
fi

# Check if Grafana is accessible
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is running at http://localhost:3000"
    echo ""
    echo "📊 Access Grafana:"
    echo "   URL: http://localhost:3000"
    echo "   Username: admin"
    echo "   Password: admin"
    echo ""
    echo "🔍 Prometheus:"
    echo "   URL: http://localhost:9090"
    echo ""
    echo "📈 Next steps:"
    echo "   1. Open Grafana at http://localhost:3000"
    echo "   2. Login with admin/admin"
    echo "   3. Go to Dashboards → Import"
    echo "   4. Check that Prometheus data source is configured"
    echo "   5. Create or import dashboards"
    echo ""
    echo "🛑 To stop monitoring:"
    echo "   docker-compose -f docker-compose.monitoring.yml down"
else
    echo "⚠️  Grafana may not be fully ready yet. Check http://localhost:3000"
fi

echo ""
echo "✨ Setup complete!"

