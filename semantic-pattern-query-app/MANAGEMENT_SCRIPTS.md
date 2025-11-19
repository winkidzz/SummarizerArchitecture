# Management Scripts Guide

Comprehensive guide for the one-command management scripts that simplify daily operations.

## Overview

Three powerful scripts for complete system lifecycle management:

1. **start-all.sh** - Start everything in correct sequence
2. **stop-all.sh** - Stop everything gracefully
3. **clean-all.sh** - Clean cache, logs, and optionally data

## Quick Reference

```bash
# Daily Workflow
./scripts/start-all.sh --skip-ingest    # Start (skip re-ingestion)
./scripts/stop-all.sh                   # Stop

# First Time / After Cleanup
./scripts/start-all.sh                  # Start with ingestion

# Maintenance
./scripts/clean-all.sh                  # Clean cache/logs
./scripts/clean-all.sh --full           # Full reset (deletes data)
```

## Detailed Documentation

### start-all.sh

**Purpose**: Complete system startup with health checks and verification

**Usage**:
```bash
# Start everything (includes document ingestion)
./scripts/start-all.sh

# Start everything (skip ingestion if already done)
./scripts/start-all.sh --skip-ingest
```

**What it does**:

1. **Checks Prerequisites**
   - Virtual environment exists
   - .env configuration file
   - Ollama service running
   - Reports status of each

2. **Starts Docker Services**
   - Elasticsearch (port 9200)
   - Qdrant (port 6333)
   - Redis (port 6380)
   - Prometheus (port 9090)
   - Grafana (port 3333)

3. **Waits for Services** (15 seconds)
   - Gives services time to initialize
   - Shows countdown progress

4. **Verifies Service Health**
   - Checks each service endpoint
   - Reports status (✅ ready, ❌ failed, ⚠️ may still be starting)
   - Exits if critical services (Elasticsearch, Qdrant) fail

5. **Ingests Documents** (unless --skip-ingest)
   - Runs scripts/ingest_patterns.py
   - Loads pattern library into vector DB
   - Required on first run or after full cleanup

6. **Starts API Server**
   - Uses scripts/start-server.sh
   - Starts on port 8000
   - Logs to /tmp/api_server.log

7. **Waits for API Ready**
   - Polls API endpoint for up to 10 seconds
   - Confirms API is responding

8. **Displays Access URLs**
   - All service URLs
   - Test command example
   - Stop command

**Exit Codes**:
- `0` - Success
- `1` - Prerequisites missing, services failed, or ingestion failed

**Example Output**:
```
🚀 Starting RAG system...

1️⃣  Checking prerequisites...
  ✅ Virtual environment found
  ✅ .env file found
  ✅ Ollama is running

2️⃣  Starting Docker services...
[docker-compose output]

3️⃣  Waiting for services to become healthy (15 seconds)...
  ⏳ 5 seconds...
  ⏳ 10 seconds...
  ✅ Services should be ready

4️⃣  Verifying Docker services...
  ✅ Elasticsearch (port 9200)
  ✅ Qdrant (port 6333)
  ✅ Redis (port 6380)
  ✅ Prometheus (port 9090)
  ✅ Grafana (port 3333)

5️⃣  Skipping document ingestion (--skip-ingest flag)

6️⃣  Starting API Server...
[API server output]

7️⃣  Waiting for API server to be ready...
  ✅ API server is ready

✅ All services started successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Quick Access Links
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 Web UI:              http://localhost:5173
  🔌 API Server:          http://localhost:8000
  📖 API Docs:            http://localhost:8000/docs
  📈 Grafana Dashboards:  http://localhost:3333
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### stop-all.sh

**Purpose**: Stop all services gracefully

**Usage**:
```bash
./scripts/stop-all.sh
```

**What it does**:

1. **Stops API Server**
   - Uses scripts/stop-server.sh
   - Kills processes on port 8000
   - Kills api_server.py by name

2. **Stops Web UI** (if running)
   - Checks for processes on port 5173
   - Kills Vite dev server

3. **Stops Docker Services**
   - Runs docker-compose down
   - Stops Elasticsearch, Qdrant, Redis, Prometheus, Grafana
   - Removes containers (but preserves volumes/data)

**Example Output**:
```
🛑 Stopping all services...

1️⃣  Stopping API Server...
  Killing process on port 8000...
  ✅ Server stopped

2️⃣  Checking for Web UI processes...
  Stopping Web UI on port 5173...
  ✅ Web UI stopped

3️⃣  Stopping Docker services...
[docker-compose down output]

✅ All services stopped!

Services stopped:
  - API Server (port 8000)
  - Web UI (port 5173)
  - Docker infrastructure
```

---

### clean-all.sh

**Purpose**: Clean cache, logs, and optionally all data

**Usage**:
```bash
# Clean cache and logs (keeps indexed data)
./scripts/clean-all.sh

# Full cleanup - deletes ALL data
./scripts/clean-all.sh --full
```

**What it does**:

**Standard Cleanup** (default):

1. **Stops All Services**
   - Runs stop-all.sh

2. **Flushes Redis Cache**
   - Runs FLUSHALL command
   - Clears semantic cache

3. **Removes Log Files**
   - Deletes /tmp/api_server.log

4. **Clears Python Cache**
   - Removes __pycache__ directories
   - Deletes *.pyc files

**Full Cleanup** (--full flag):

5. **Removes Docker Volumes** (with confirmation)
   - Prompts for confirmation
   - Deletes ALL indexed documents
   - Deletes vector embeddings
   - Requires re-ingestion

**Example Output** (standard):
```
🧹 Cleaning RAG system...

1️⃣  Stopping all services...
[stop-all.sh output]

2️⃣  Clearing cache data...
  Flushing Redis cache...
  ✅ Redis cache flushed

3️⃣  Clearing log files...
  ✅ Removed /tmp/api_server.log

4️⃣  Clearing Python cache...
  ✅ Python cache cleared

5️⃣  Skipping Docker volume removal (use --full flag to remove)

✅ Cleanup complete!

What was cleaned:
  - API Server stopped
  - Web UI stopped
  - Docker services stopped
  - Redis cache flushed
  - Log files removed
  - Python cache cleared
```

**Example Output** (--full):
```
[... same as above ...]

5️⃣  FULL CLEAN: Removing Docker volumes...
  ⚠️  WARNING: This will delete all indexed data!
  You will need to re-run: python scripts/ingest_patterns.py

  Continue? (y/N): y
  ✅ Docker volumes removed

  ⚠️  Remember to re-ingest documents:
     docker-compose up -d
     python scripts/ingest_patterns.py

✅ Cleanup complete!

What was cleaned:
  [... same as above ...]
  - Docker volumes removed (FULL CLEAN)
```

---

## Common Workflows

### Daily Development

```bash
# Morning - start work
./scripts/start-all.sh --skip-ingest

# Work on code...

# Evening - stop work
./scripts/stop-all.sh
```

### First Time Setup

```bash
# Start with document ingestion
./scripts/start-all.sh
```

### After Code Changes

```bash
# Restart API server only (faster)
./scripts/stop-server.sh
./scripts/start-server.sh

# OR restart everything
./scripts/stop-all.sh
./scripts/start-all.sh --skip-ingest
```

### Troubleshooting / Reset

```bash
# Clean cache and logs
./scripts/clean-all.sh

# Full system reset
./scripts/clean-all.sh --full
./scripts/start-all.sh  # Will re-ingest automatically
```

### Weekly Maintenance

```bash
# Clear accumulated cache/logs
./scripts/clean-all.sh
./scripts/start-all.sh --skip-ingest
```

---

## Troubleshooting

### "Virtual environment not found"

**Solution**: Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "Ollama not running or not accessible"

**Solution**: Start Ollama service
```bash
ollama serve
```

### "Some critical services failed to start"

**Possible causes**:
- Docker not running
- Ports already in use
- Insufficient memory

**Solution**: Check Docker status
```bash
docker ps
docker-compose logs
```

### "API server failed to start"

**Solution**: Check logs
```bash
cat /tmp/api_server.log
```

### Services slow to start

**Normal behavior**: Services may take 15-30 seconds to fully initialize. The script waits 15 seconds and verifies endpoints.

---

## Advanced Usage

### Custom API Port

```bash
# Edit .ports file
echo "API_PORT=8001" > .ports

# Start with custom port
./scripts/start-all.sh --skip-ingest
```

### Background Execution

```bash
# Not recommended - loses output
nohup ./scripts/start-all.sh --skip-ingest > startup.log 2>&1 &
```

### Automated Startup

Add to shell profile for automatic startup:

```bash
# ~/.bashrc or ~/.zshrc
alias rag-start="cd /path/to/semantic-pattern-query-app && ./scripts/start-all.sh --skip-ingest"
alias rag-stop="cd /path/to/semantic-pattern-query-app && ./scripts/stop-all.sh"
alias rag-clean="cd /path/to/semantic-pattern-query-app && ./scripts/clean-all.sh"
```

---

## Script Locations

```
semantic-pattern-query-app/
├── scripts/
│   ├── start-all.sh      # Complete startup
│   ├── stop-all.sh       # Complete shutdown
│   ├── clean-all.sh      # Cleanup
│   ├── start-server.sh   # API server only (used by start-all.sh)
│   └── stop-server.sh    # API server only (used by stop-all.sh)
```

---

## Related Documentation

- [README.md](README.md) - Main project documentation
- [docs/PORTS.md](docs/PORTS.md) - Port configuration details
- [docs/guides/QUICKSTART.md](docs/guides/QUICKSTART.md) - Step-by-step setup guide
- [CHANGELOG.md](CHANGELOG.md) - Complete change history

---

**Last Updated**: 2025-11-18
