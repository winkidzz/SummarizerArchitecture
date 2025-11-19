#!/bin/bash
# Clean all services (data, cache, logs)
# Usage: ./scripts/clean-all.sh [--full]
#   --full: Also removes Docker volumes (WARNING: Deletes all indexed data)

FULL_CLEAN=false
if [ "$1" == "--full" ]; then
    FULL_CLEAN=true
fi

echo "🧹 Cleaning RAG system..."
echo ""

# Stop all services first
echo "1️⃣  Stopping all services..."
./scripts/stop-all.sh
echo ""

# Clear cache data
echo "2️⃣  Clearing cache data..."
if docker ps -a --format '{{.Names}}' | grep -q 'redis'; then
    echo "  Flushing Redis cache..."
    docker exec semantic-pattern-query-app-redis-1 redis-cli FLUSHALL 2>/dev/null || echo "  Redis not running, skipping..."
else
    echo "  Redis not running, skipping..."
fi
echo ""

# Clear logs
echo "3️⃣  Clearing log files..."
if [ -f /tmp/api_server.log ]; then
    rm /tmp/api_server.log
    echo "  ✅ Removed /tmp/api_server.log"
else
    echo "  No log file found"
fi
echo ""

# Clear Python cache
echo "4️⃣  Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "  ✅ Python cache cleared"
echo ""

# Full clean (Docker volumes)
if [ "$FULL_CLEAN" = true ]; then
    echo "5️⃣  FULL CLEAN: Removing Docker volumes..."
    echo "  ⚠️  WARNING: This will delete all indexed data!"
    echo "  You will need to re-run: python scripts/ingest_patterns.py"
    echo ""
    read -p "  Continue? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        echo "  ✅ Docker volumes removed"
        echo ""
        echo "  ⚠️  Remember to re-ingest documents:"
        echo "     docker-compose up -d"
        echo "     python scripts/ingest_patterns.py"
    else
        echo "  Skipping volume removal"
    fi
else
    echo "5️⃣  Skipping Docker volume removal (use --full flag to remove)"
fi
echo ""

echo "✅ Cleanup complete!"
echo ""
echo "What was cleaned:"
echo "  - API Server stopped"
echo "  - Web UI stopped"
echo "  - Docker services stopped"
echo "  - Redis cache flushed"
echo "  - Log files removed"
echo "  - Python cache cleared"
if [ "$FULL_CLEAN" = true ]; then
    echo "  - Docker volumes removed (FULL CLEAN)"
fi
echo ""
