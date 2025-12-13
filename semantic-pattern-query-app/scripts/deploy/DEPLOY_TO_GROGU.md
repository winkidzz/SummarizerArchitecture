# Deploy Elasticsearch and Redis to Grogu Server

This guide explains how to install Elasticsearch 8.19.7 and Redis 7.2-alpine on the grogu server with user `winkidzz`.

## Prerequisites

1. SSH access to grogu server as `winkidzz` user
2. Docker and Docker Compose installed on grogu server
3. User `winkidzz` must be in the `docker` group

## Quick Installation

### Option 1: Automated Script (Recommended)

1. **Copy the installation script to grogu server:**

```bash
# From your local machine
scp scripts/deploy/install-services-grogu.sh winkidzz@grogu:~/install-services.sh
```

2. **SSH into grogu server:**

```bash
ssh winkidzz@grogu
```

3. **Run the installation script:**

```bash
chmod +x ~/install-services.sh
~/install-services.sh
```

The script will:
- Check Docker installation
- Create docker-compose.yml in `~/docker-services/`
- Pull the required images
- Start Elasticsearch and Redis
- Verify services are running

### Option 2: Manual Installation

1. **SSH into grogu server:**

```bash
ssh winkidzz@grogu
```

2. **Create directory for services:**

```bash
mkdir -p ~/docker-services
cd ~/docker-services
```

3. **Copy docker-compose file:**

```bash
# Copy from your local machine
scp scripts/deploy/docker-compose-grogu.yml winkidzz@grogu:~/docker-services/docker-compose.yml
```

Or create it manually:

```bash
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
      - "6380:6379"
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
```

4. **Start services:**

```bash
docker-compose up -d
```

5. **Verify services are running:**

```bash
# Check Elasticsearch
curl http://localhost:9200/_cluster/health

# Check Redis
docker exec semantic-redis redis-cli ping
```

## Service Management

### Start Services

```bash
cd ~/docker-services
docker-compose up -d
```

### Stop Services

```bash
cd ~/docker-services
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f elasticsearch
docker-compose logs -f redis
```

### Check Status

```bash
docker-compose ps
```

### Restart Services

```bash
docker-compose restart
```

## Service Endpoints

- **Elasticsearch**: `http://localhost:9200` (or `http://grogu:9200` from other machines)
- **Redis**: `localhost:6380` (external) or `localhost:6379` (internal container)

## Configuration Details

### Elasticsearch 8.19.7
- **Memory**: 256MB heap (min/max), 768MB container limit
- **Security**: Disabled (xpack.security.enabled=false)
- **ML**: Disabled (xpack.ml.enabled=false)
- **Mode**: Single-node cluster
- **Ports**: 9200 (HTTP API), 9300 (cluster communication)

### Redis 7.2-alpine
- **Image**: redis:7.2-alpine (lightweight Alpine-based)
- **Port**: 6380 external → 6379 internal
- **Persistence**: Data stored in Docker volume

## Troubleshooting

### Docker Permission Issues

If you get permission denied errors:

```bash
# Add user to docker group
sudo usermod -aG docker winkidzz

# Apply changes (log out and back in, or):
newgrp docker
```

### Port Already in Use

If ports 9200, 9300, or 6380 are already in use:

```bash
# Check what's using the port
sudo lsof -i :9200
sudo lsof -i :6380

# Stop conflicting services or modify ports in docker-compose.yml
```

### Elasticsearch Not Starting

Check logs:

```bash
docker logs semantic-elasticsearch
```

Common issues:
- **Out of memory**: Increase `mem_limit` in docker-compose.yml
- **Port conflict**: Check if port 9200 is already in use
- **Volume permissions**: Ensure Docker has write access to volumes

### Redis Not Starting

Check logs:

```bash
docker logs semantic-redis
```

## Verification

After installation, verify services are working:

```bash
# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Elasticsearch info
curl http://localhost:9200/

# Redis ping
docker exec semantic-redis redis-cli ping

# Redis info
docker exec semantic-redis redis-cli info
```

Expected output:
- Elasticsearch: `{"status":"green"}` or `{"status":"yellow"}` (yellow is normal for single-node)
- Redis: `PONG`

## Next Steps

After services are running, you can:

1. **Configure your application** to connect to:
   - `ELASTICSEARCH_URL=http://grogu:9200` (or IP address)
   - `REDIS_HOST=grogu` (or IP address)
   - `REDIS_PORT=6380`

2. **Set up firewall rules** if accessing from remote machines:
   ```bash
   # Allow Elasticsearch (if using firewall)
   sudo ufw allow 9200/tcp
   sudo ufw allow 9300/tcp
   
   # Allow Redis (if using firewall)
   sudo ufw allow 6380/tcp
   ```

3. **Monitor services**:
   ```bash
   # Watch logs
   docker-compose logs -f
   
   # Check resource usage
   docker stats
   ```

