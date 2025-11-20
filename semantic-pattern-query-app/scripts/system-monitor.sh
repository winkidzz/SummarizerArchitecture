#!/bin/bash

###############################################################################
# System Monitor & Manager
#
# Monitors and manages all system dependencies for the RAG application
#
# Usage:
#   ./scripts/system-monitor.sh status     - Check health of all services
#   ./scripts/system-monitor.sh start      - Start all services
#   ./scripts/system-monitor.sh stop       - Stop all services
#   ./scripts/system-monitor.sh restart    - Restart all services
#   ./scripts/system-monitor.sh monitor    - Continuous monitoring (Ctrl+C to exit)
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

###############################################################################
# Health Check Functions
###############################################################################

check_ollama() {
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:11434/api/tags" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama is ${GREEN}UP${NC} (http://localhost:11434)"
        if pgrep -f "ollama" > /dev/null; then
            echo -e "  ${BLUE}ℹ${NC} Process: PID $(pgrep -f 'ollama' | head -1)"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} Ollama is ${RED}DOWN${NC}"
        return 1
    fi
}

check_qdrant() {
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:6333/collections" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Qdrant is ${GREEN}UP${NC} (http://localhost:6333)"
        if lsof -i :6333 > /dev/null 2>&1; then
            echo -e "  ${BLUE}ℹ${NC} Port 6333 is in use"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} Qdrant is ${RED}DOWN${NC}"
        return 1
    fi
}

check_elasticsearch() {
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:9200/_cluster/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Elasticsearch is ${GREEN}UP${NC} (http://localhost:9200)"
        if lsof -i :9200 > /dev/null 2>&1; then
            echo -e "  ${BLUE}ℹ${NC} Port 9200 is in use"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} Elasticsearch is ${RED}DOWN${NC}"
        return 1
    fi
}

check_redis() {
    # Try redis-cli first, fallback to docker exec
    local redis_ok=false

    if command -v redis-cli > /dev/null 2>&1; then
        redis-cli -p 6380 ping > /dev/null 2>&1 && redis_ok=true
    else
        # redis-cli not installed, try docker exec
        local redis_container=$(docker ps --format '{{.Names}}' | grep -E '^(redis|semantic-redis)' | head -1)
        if [ -n "$redis_container" ]; then
            docker exec "$redis_container" redis-cli ping > /dev/null 2>&1 && redis_ok=true
        fi
    fi

    if [ "$redis_ok" = true ]; then
        echo -e "${GREEN}✓${NC} Redis is ${GREEN}UP${NC} (localhost:6380)"
        if lsof -i :6380 > /dev/null 2>&1; then
            echo -e "  ${BLUE}ℹ${NC} Port 6380 is in use"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} Redis is ${RED}DOWN${NC}"
        if lsof -i :6380 > /dev/null 2>&1; then
            echo -e "  ${YELLOW}⚠${NC} Port 6380 is in use but not responding"
        fi
        return 1
    fi
}

check_api_server() {
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API Server is ${GREEN}UP${NC} (http://localhost:8000)"
        if pgrep -f "api_server.py" > /dev/null; then
            echo -e "  ${BLUE}ℹ${NC} Process: PID $(pgrep -f 'api_server.py' | head -1)"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} API Server is ${RED}DOWN${NC}"
        if pgrep -f "api_server.py" > /dev/null; then
            echo -e "  ${YELLOW}⚠${NC} Process running but not responding"
        fi
        return 1
    fi
}

check_ui_server() {
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:5173/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} UI Server is ${GREEN}UP${NC} (http://localhost:5173)"
        if lsof -i :5173 > /dev/null 2>&1; then
            echo -e "  ${BLUE}ℹ${NC} Port 5173 is in use"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} UI Server is ${RED}DOWN${NC}"
        if lsof -i :5173 > /dev/null 2>&1; then
            echo -e "  ${YELLOW}⚠${NC} Port 5173 is in use but not responding"
        fi
        return 1
    fi
}

###############################################################################
# Service Start Functions
###############################################################################

start_ollama() {
    echo -e "${BLUE}→${NC} Starting Ollama..."
    if pgrep -f "ollama" > /dev/null; then
        echo -e "${YELLOW}⚠${NC} Ollama already running"
        return 0
    fi

    if [ "$(uname)" == "Darwin" ]; then
        # macOS
        open -a Ollama 2>/dev/null || {
            echo -e "${YELLOW}⚠${NC} Ollama app not found, trying command line..."
            ollama serve > /dev/null 2>&1 &
        }
    else
        # Linux
        ollama serve > /dev/null 2>&1 &
    fi

    sleep 3
    if pgrep -f "ollama" > /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama started"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start Ollama"
        return 1
    fi
}

start_qdrant() {
    echo -e "${BLUE}→${NC} Starting Qdrant..."

    if curl -s "http://localhost:6333" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Qdrant already running"
        return 0
    fi

    if docker ps -a | grep qdrant > /dev/null; then
        docker start qdrant > /dev/null 2>&1
    else
        docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant > /dev/null 2>&1
    fi

    sleep 3
    if curl -s "http://localhost:6333" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Qdrant started"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start Qdrant"
        return 1
    fi
}

start_elasticsearch() {
    echo -e "${BLUE}→${NC} Starting Elasticsearch..."

    if curl -s "http://localhost:9200" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Elasticsearch already running"
        return 0
    fi

    if docker ps -a | grep elasticsearch > /dev/null; then
        docker start elasticsearch > /dev/null 2>&1
    else
        docker run -d -p 9200:9200 -p 9300:9300 \
            -e "discovery.type=single-node" \
            -e "xpack.security.enabled=false" \
            --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:8.11.0 > /dev/null 2>&1
    fi

    sleep 5
    if curl -s "http://localhost:9200" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Elasticsearch started"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start Elasticsearch"
        return 1
    fi
}

start_redis() {
    echo -e "${BLUE}→${NC} Starting Redis..."

    # Check if already running (try redis-cli or docker exec)
    local redis_running=false
    if command -v redis-cli > /dev/null 2>&1 && redis-cli -p 6380 ping > /dev/null 2>&1; then
        redis_running=true
    else
        local redis_container=$(docker ps --format '{{.Names}}' | grep -E '^(redis|semantic-redis)' | head -1)
        if [ -n "$redis_container" ] && docker exec "$redis_container" redis-cli ping > /dev/null 2>&1; then
            redis_running=true
        fi
    fi

    if [ "$redis_running" = true ]; then
        echo -e "${YELLOW}⚠${NC} Redis already running"
        return 0
    fi

    # Try to find existing Redis container (multiple possible names)
    local redis_container=$(docker ps -a --format '{{.Names}}' | grep -E '^(redis|semantic-redis)' | head -1)

    if [ -n "$redis_container" ]; then
        echo -e "  ${BLUE}ℹ${NC} Found container: $redis_container"
        docker start "$redis_container" > /dev/null 2>&1
    else
        echo -e "  ${BLUE}ℹ${NC} Creating new Redis container"
        docker run -d -p 6380:6379 --name semantic-redis redis:alpine > /dev/null 2>&1
    fi

    sleep 2
    if redis-cli -p 6380 ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis started"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start Redis"
        echo -e "  ${YELLOW}ℹ${NC} Try: docker logs $redis_container"
        return 1
    fi
}

start_api_server() {
    echo -e "${BLUE}→${NC} Starting API Server..."

    if pgrep -f "api_server.py" > /dev/null; then
        echo -e "${YELLOW}⚠${NC} API Server already running"
        return 0
    fi

    cd "$APP_DIR"
    if [ -f "scripts/start-server.sh" ]; then
        ./scripts/start-server.sh > /dev/null 2>&1 &
        sleep 5
        if pgrep -f "api_server.py" > /dev/null; then
            echo -e "${GREEN}✓${NC} API Server started"
            return 0
        else
            echo -e "${RED}✗${NC} Failed to start API Server"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} start-server.sh not found"
        return 1
    fi
}

start_ui_server() {
    echo -e "${BLUE}→${NC} Starting UI Server..."

    if lsof -i :5173 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} UI Server already running"
        return 0
    fi

    # Try web-ui directory first (correct location), then fallback to summarizer-ui
    local ui_dir="$APP_DIR/web-ui"
    if [ ! -d "$ui_dir" ]; then
        ui_dir="$(dirname "$APP_DIR")/summarizer-ui"
        if [ ! -d "$ui_dir" ]; then
            echo -e "${RED}✗${NC} UI directory not found"
            echo -e "  ${YELLOW}ℹ${NC} Tried: $APP_DIR/web-ui and $(dirname "$APP_DIR")/summarizer-ui"
            return 1
        fi
    fi

    echo -e "  ${BLUE}ℹ${NC} Using UI directory: $ui_dir"
    cd "$ui_dir"

    if [ ! -d "node_modules" ]; then
        echo -e "${RED}✗${NC} UI dependencies not installed"
        echo -e "  ${YELLOW}ℹ${NC} Run: cd $ui_dir && npm install"
        return 1
    fi

    npm run dev > /tmp/ui_server.log 2>&1 &
    local npm_pid=$!
    sleep 3

    if lsof -i :5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} UI Server started (PID: $npm_pid)"
        echo -e "  ${BLUE}ℹ${NC} Access at: http://localhost:5173"
        return 0
    else
        echo -e "${RED}✗${NC} Failed to start UI Server"
        echo -e "  ${YELLOW}ℹ${NC} Check /tmp/ui_server.log for errors"
        return 1
    fi
}

###############################################################################
# Service Stop Functions
###############################################################################

stop_ollama() {
    echo -e "${BLUE}→${NC} Stopping Ollama..."
    pkill -f "ollama" 2>/dev/null && echo -e "${GREEN}✓${NC} Ollama stopped" || echo -e "${YELLOW}⚠${NC} Ollama not running"
}

stop_qdrant() {
    echo -e "${BLUE}→${NC} Stopping Qdrant..."
    docker stop qdrant 2>/dev/null && echo -e "${GREEN}✓${NC} Qdrant stopped" || echo -e "${YELLOW}⚠${NC} Qdrant not running"
}

stop_elasticsearch() {
    echo -e "${BLUE}→${NC} Stopping Elasticsearch..."
    docker stop elasticsearch 2>/dev/null && echo -e "${GREEN}✓${NC} Elasticsearch stopped" || echo -e "${YELLOW}⚠${NC} Elasticsearch not running"
}

stop_redis() {
    echo -e "${BLUE}→${NC} Stopping Redis..."
    local redis_container=$(docker ps --format '{{.Names}}' | grep -E '^(redis|semantic-redis)' | head -1)
    if [ -n "$redis_container" ]; then
        docker stop "$redis_container" 2>/dev/null && echo -e "${GREEN}✓${NC} Redis stopped" || echo -e "${YELLOW}⚠${NC} Redis not running"
    else
        echo -e "${YELLOW}⚠${NC} Redis not running"
    fi
}

stop_api_server() {
    echo -e "${BLUE}→${NC} Stopping API Server..."
    pkill -f "api_server.py" 2>/dev/null && echo -e "${GREEN}✓${NC} API Server stopped" || echo -e "${YELLOW}⚠${NC} API Server not running"
}

stop_ui_server() {
    echo -e "${BLUE}→${NC} Stopping UI Server..."
    # Kill process on port 5173
    lsof -ti :5173 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓${NC} UI Server stopped" || echo -e "${YELLOW}⚠${NC} UI Server not running"
}

###############################################################################
# Main Commands
###############################################################################

status_check() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  System Status Check${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    local services_up=0

    check_ollama && ((services_up++))
    echo ""

    check_qdrant && ((services_up++))
    echo ""

    check_elasticsearch && ((services_up++))
    echo ""

    check_redis && ((services_up++))
    echo ""

    check_api_server && ((services_up++))
    echo ""

    check_ui_server && ((services_up++))
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    if [ $services_up -eq 6 ]; then
        echo -e "${GREEN}✓ All services are running ($services_up/6)${NC}"
    else
        echo -e "${YELLOW}⚠ $services_up/6 services are running${NC}"
        echo -e "${YELLOW}  Run './scripts/system-monitor.sh start' to start missing services${NC}"
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    return $((6 - services_up))
}

start_all() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Starting Services${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    local services_started=0

    # Check and start each service only if it's down
    echo -e "${BLUE}→${NC} Checking Ollama..."
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:11434/api/tags" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama already running"
    else
        start_ollama && ((services_started++))
    fi

    echo -e "\n${BLUE}→${NC} Checking Qdrant..."
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:6333/collections" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Qdrant already running"
    else
        start_qdrant && ((services_started++))
    fi

    echo -e "\n${BLUE}→${NC} Checking Elasticsearch..."
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:9200/_cluster/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Elasticsearch already running"
    else
        start_elasticsearch && ((services_started++))
    fi

    echo -e "\n${BLUE}→${NC} Checking Redis..."
    if redis-cli -p 6380 ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis already running"
    else
        start_redis && ((services_started++))
    fi

    echo -e "\n${BLUE}→${NC} Checking API Server..."
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API Server already running"
    else
        start_api_server && ((services_started++))
    fi

    echo -e "\n${BLUE}→${NC} Checking UI Server..."
    if curl -s --connect-timeout 2 --max-time 5 "http://localhost:5173/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} UI Server already running"
    else
        start_ui_server && ((services_started++))
    fi

    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    if [ $services_started -eq 0 ]; then
        echo -e "${GREEN}✓ All services were already running${NC}"
    else
        echo -e "${GREEN}✓ Started $services_started service(s)${NC}"
        echo -e "${YELLOW}  Waiting 10 seconds for services to initialize...${NC}"
        sleep 10
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    status_check
}

stop_all() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Stopping All Services${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    stop_ui_server
    stop_api_server
    stop_redis
    stop_elasticsearch
    stop_qdrant
    stop_ollama

    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ All services stopped${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"
}

restart_all() {
    stop_all
    echo -e "\n${YELLOW}Waiting 5 seconds before restart...${NC}\n"
    sleep 5
    start_all
}

continuous_monitor() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Continuous Monitoring Mode${NC}"
    echo -e "${BLUE}  Press Ctrl+C to exit${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

    while true; do
        clear
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
        echo -e "${BLUE}  System Monitor - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
        echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

        status_check

        echo -e "${YELLOW}Refreshing in 30 seconds... (Ctrl+C to exit)${NC}\n"
        sleep 30
    done
}

show_help() {
    cat << EOF

${BLUE}System Monitor & Manager${NC}
Monitors and manages all RAG application dependencies

${YELLOW}Usage:${NC}
  $0 [command]

${YELLOW}Commands:${NC}
  ${GREEN}status${NC}     Check health of all services (default)
  ${GREEN}start${NC}      Start all services
  ${GREEN}stop${NC}       Stop all services
  ${GREEN}restart${NC}    Restart all services
  ${GREEN}monitor${NC}    Continuous monitoring (refreshes every 30s)
  ${GREEN}help${NC}       Show this help message

${YELLOW}Services Monitored:${NC}
  • Ollama         - http://localhost:11434 (LLM & embeddings)
  • Qdrant         - http://localhost:6333 (vector database)
  • Elasticsearch  - http://localhost:9200 (search engine)
  • Redis          - localhost:6380 (cache)
  • API Server     - http://localhost:8000 (RAG API)
  • UI Server      - http://localhost:5173 (web interface)

${YELLOW}Examples:${NC}
  $0 status          # Check all services
  $0 start           # Start everything
  $0 stop            # Stop everything
  $0 monitor         # Watch services continuously

${YELLOW}Quick Actions:${NC}
  Start UI only:     cd web-ui && npm run dev
  Start API only:    ./scripts/start-server.sh
  View API logs:     tail -f logs/*.log
  View UI logs:      tail -f /tmp/ui_server.log

EOF
}

###############################################################################
# Main Entry Point
###############################################################################

main() {
    local command=${1:-status}

    case "$command" in
        status)
            status_check
            ;;
        start)
            start_all
            ;;
        stop)
            stop_all
            ;;
        restart)
            restart_all
            ;;
        monitor)
            continuous_monitor
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$command'${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
