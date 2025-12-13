#!/bin/bash
# Install Elasticsearch 8.19.7 and Redis 7.2-alpine on grogu server
# Usage: Run this script on the grogu server as winkidzz user

set -e

echo "🚀 Installing Elasticsearch 8.19.7 and Redis 7.2-alpine on grogu server"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as correct user
if [ "$USER" != "winkidzz" ]; then
    echo -e "${YELLOW}⚠️  Warning: Not running as winkidzz user (current: $USER)${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Docker is installed
echo "1️⃣  Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo "  sudo usermod -aG docker winkidzz"
    echo "  newgrp docker  # or log out and back in"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Check if user is in docker group
if ! groups | grep -q docker; then
    echo -e "${YELLOW}⚠️  User not in docker group${NC}"
    echo "You may need to run: sudo usermod -aG docker winkidzz"
    echo "Then log out and back in, or run: newgrp docker"
fi

# Create directory for docker-compose file
COMPOSE_DIR="$HOME/docker-services"
mkdir -p "$COMPOSE_DIR"
cd "$COMPOSE_DIR"

echo ""
echo "2️⃣  Creating docker-compose.yml..."

# Create docker-compose.yml file
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
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
    restart: unless-stopped

  redis:
    image: redis:7.2-alpine
    container_name: semantic-redis
    ports:
      - "6380:6379"  # Use port 6380 externally, 6379 internally
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

volumes:
  elasticsearch_data:
  redis_data:
EOF

echo -e "${GREEN}✅ docker-compose.yml created at $COMPOSE_DIR/docker-compose.yml${NC}"

echo ""
echo "3️⃣  Pulling Docker images..."
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.19.7
docker pull redis:7.2-alpine
echo -e "${GREEN}✅ Images pulled successfully${NC}"

echo ""
echo "4️⃣  Starting services..."
docker-compose up -d

echo ""
echo "5️⃣  Waiting for services to be ready..."
sleep 10

# Wait for Elasticsearch
echo "  - Waiting for Elasticsearch..."
MAX_WAIT=60
WAIT_COUNT=0
while ! curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Elasticsearch failed to start within $MAX_WAIT seconds${NC}"
        echo "Check logs with: docker logs semantic-elasticsearch"
        exit 1
    fi
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
    echo -n "."
done
echo ""
echo -e "${GREEN}  ✅ Elasticsearch is ready${NC}"

# Wait for Redis
echo "  - Waiting for Redis..."
MAX_WAIT=30
WAIT_COUNT=0
while ! docker exec semantic-redis redis-cli ping > /dev/null 2>&1; do
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        echo -e "${RED}❌ Redis failed to start within $MAX_WAIT seconds${NC}"
        echo "Check logs with: docker logs semantic-redis"
        exit 1
    fi
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo -n "."
done
echo ""
echo -e "${GREEN}  ✅ Redis is ready${NC}"

echo ""
echo "6️⃣  Verifying services..."

# Check Elasticsearch
ES_HEALTH=$(curl -s http://localhost:9200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
echo "  - Elasticsearch cluster status: $ES_HEALTH"
if [ "$ES_HEALTH" != "green" ] && [ "$ES_HEALTH" != "yellow" ]; then
    echo -e "${YELLOW}  ⚠️  Elasticsearch status is $ES_HEALTH (expected green or yellow)${NC}"
fi

# Check Redis
REDIS_PING=$(docker exec semantic-redis redis-cli ping)
echo "  - Redis ping: $REDIS_PING"

echo ""
echo -e "${GREEN}✅ Installation complete!${NC}"
echo ""
echo "Services are running:"
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Redis: localhost:6380 (external) -> 6379 (internal)"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Start services: docker-compose up -d"
echo "  - Check status: docker-compose ps"
echo ""
echo "Configuration location: $COMPOSE_DIR"

