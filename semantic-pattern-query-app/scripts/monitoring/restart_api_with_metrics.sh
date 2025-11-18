#!/bin/bash
# Restart API server and test quality metrics

echo "🔄 Restarting API server with quality metrics..."
echo ""

# Stop existing API server
echo "1. Stopping existing API server..."
pkill -f "api_server.py"
sleep 3

# Start API server in background
echo "2. Starting API server..."
cd /Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app

# Check if venv exists
if [ -d "venv" ]; then
    ./venv/bin/python3 src/api_server.py > /tmp/api_server.log 2>&1 &
else
    python3 src/api_server.py > /tmp/api_server.log 2>&1 &
fi

API_PID=$!
echo "   API server started (PID: $API_PID)"
echo "   Logs: tail -f /tmp/api_server.log"

# Wait for server to be ready
echo ""
echo "3. Waiting for server to be ready..."
max_attempts=20
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Server is ready!"
        break
    fi
    echo "   Waiting... (attempt $((attempt+1))/$max_attempts)"
    sleep 2
    attempt=$((attempt+1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "   ❌ Server did not start. Check logs: tail -f /tmp/api_server.log"
    exit 1
fi

# Send test queries
echo ""
echo "4. Sending test queries..."

queries=(
    "What is RAPTOR RAG?"
    "Explain contextual retrieval"
    "What are the benefits of hybrid search?"
    "Describe HyDE RAG technique"
    "What is query routing in RAG?"
)

for i in "${!queries[@]}"; do
    query_num=$((i+1))
    query="${queries[$i]}"
    echo "   Query $query_num/5: ${query:0:40}..."

    response=$(curl -s -X POST http://localhost:8000/query \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"top_k\": 3}" \
        --max-time 30)

    # Check if quality_metrics exists
    has_metrics=$(echo "$response" | jq -r '.quality_metrics != null' 2>/dev/null)

    if [ "$has_metrics" = "true" ]; then
        faithfulness=$(echo "$response" | jq -r '.quality_metrics.answer.faithfulness' 2>/dev/null)
        hallucination=$(echo "$response" | jq -r '.quality_metrics.answer.has_hallucination' 2>/dev/null)
        echo "      ✅ Quality metrics: Faithfulness=${faithfulness}, Hallucination=${hallucination}"
    else
        echo "      ⚠️  No quality metrics in response"
    fi

    sleep 2
done

# Check Prometheus metrics
echo ""
echo "5. Checking Prometheus metrics..."

metrics_response=$(curl -s http://localhost:8000/metrics)

if echo "$metrics_response" | grep -q "rag_answer_faithfulness_score"; then
    count=$(echo "$metrics_response" | grep "rag_answer_faithfulness_score_count" | awk '{print $2}')
    echo "   ✅ Quality metrics found in Prometheus"
    echo "      Faithfulness samples collected: $count"
else
    echo "   ⚠️  Quality metrics not found in Prometheus"
fi

if echo "$metrics_response" | grep -q "rag_context_relevancy"; then
    echo "   ✅ Context metrics found in Prometheus"
else
    echo "   ⚠️  Context metrics not found in Prometheus"
fi

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 View Quality Metrics Dashboard:"
echo "   http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics"
echo ""
echo "🔍 Check Prometheus Metrics:"
echo "   http://localhost:9090"
echo "   Query: rag_answer_faithfulness_score"
echo ""
echo "📝 API Server Logs:"
echo "   tail -f /tmp/api_server.log"
echo ""
echo "🧪 Test API:"
echo "   curl -X POST http://localhost:8000/query \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"test\", \"top_k\": 3}' | jq '.quality_metrics'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
