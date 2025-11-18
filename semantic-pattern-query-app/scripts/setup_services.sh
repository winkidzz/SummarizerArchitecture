#!/bin/bash
# Setup script for Elasticsearch, Qdrant, and Redis

set -e

echo "🚀 Setting up services for Semantic Pattern Query App..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Start services
echo "📦 Starting services with docker-compose..."
cd "$(dirname "$0")/.."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."

# Wait for Qdrant
echo "  - Waiting for Qdrant..."
until curl -s http://localhost:6333/health > /dev/null 2>&1; do
    sleep 1
done
echo "  ✅ Qdrant is ready"

# Wait for Elasticsearch
echo "  - Waiting for Elasticsearch..."
until curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    sleep 1
done
echo "  ✅ Elasticsearch is ready"

# Wait for Redis
echo "  - Waiting for Redis..."
until redis-cli -h localhost ping > /dev/null 2>&1; do
    sleep 1
done
echo "  ✅ Redis is ready"

echo ""
echo "✅ All services are ready!"
echo ""
echo "Services:"
echo "  - Qdrant: http://localhost:6333"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Redis: localhost:6379"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Pull Qwen model: ollama pull qwen3:14b"
echo "  3. Run ingestion: python scripts/ingest_patterns.py"

