# Quality Metrics Troubleshooting Guide

## Issue: Quality Metrics Not Showing in Dashboard

### Problem

After implementing real-time quality metrics, you may not see them in the Grafana dashboard immediately.

### Root Cause

The API server needs to be **restarted** to pick up the new code changes in `api_server.py`.

## Solution: Restart API Server

### Step 1: Stop the Current API Server

```bash
# Find the API server process
ps aux | grep "api_server.py" | grep -v grep

# Kill the process (replace PID with actual process ID from above)
kill <PID>

# Or use pkill
pkill -f api_server.py
```

### Step 2: Restart the API Server

```bash
cd /Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app

# Activate virtual environment (if using venv)
source venv/bin/activate

# Start API server
python3 src/api_server.py

# Or if using venv Python
./venv/bin/python3 src/api_server.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Verify Quality Metrics Are Working

#### Option 1: Quick Test with Curl

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAPTOR RAG?", "top_k": 3}' | jq '.quality_metrics'
```

**Expected output**:
```json
{
  "answer": {
    "faithfulness": 0.95,
    "relevancy": 0.88,
    "completeness": 0.80,
    "has_hallucination": false,
    "hallucination_severity": "minor"
  },
  "context": {
    "relevancy": 0.87,
    "utilization": 0.75
  }
}
```

If you get `null` or the request times out, there's an issue with the code.

#### Option 2: Run the Test Script

```bash
cd semantic-pattern-query-app
python3 test_api_quality_metrics.py
```

This will:
- Send 3 test queries
- Display quality metrics for each
- Check Prometheus metrics endpoint
- Show summary of results

**Expected output**:
```
================================================================================
Test Query #1: What is RAPTOR RAG and how does it work?
================================================================================

✅ Query successful!
Answer length: 450 chars
Sources retrieved: 5

📊 Quality Metrics:

  Answer Quality:
    Faithfulness:    95.00%
    Relevancy:       88.00%
    Completeness:    80.00%
    Hallucination:   False
    Severity:        minor

  Context Quality:
    Relevancy:       87.00%
    Utilization:     75.00%
```

#### Option 3: Check Prometheus Metrics

```bash
curl http://localhost:8000/metrics | grep rag_answer
```

**Expected output**:
```
rag_answer_faithfulness_score_bucket{le="0.0"} 0.0
rag_answer_faithfulness_score_bucket{le="0.2"} 0.0
rag_answer_faithfulness_score_bucket{le="0.4"} 0.0
rag_answer_faithfulness_score_count 3
rag_answer_faithfulness_score_sum 2.85
```

### Step 4: View in Grafana Dashboard

1. **Send some queries** to generate metrics (at least 3-5 queries)

2. **Open the Quality Metrics Dashboard**:
   http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics

3. **Wait 30 seconds** (dashboard refresh interval)

4. **Check these panels**:
   - "Overall Quality Score" (top left)
   - "Answer Faithfulness" gauge
   - "Hallucination Rate" stat
   - "Context Relevancy" gauge

5. If panels show "No data":
   - Click the time range selector (top right)
   - Change to "Last 5 minutes" or "Last 15 minutes"
   - Click "Refresh" button

## Common Issues

### Issue 1: API Request Timeouts

**Symptom**: Queries take >30 seconds and timeout

**Causes**:
1. Quality evaluation code has errors
2. Ollama generation model is slow
3. Database connection issues

**Solution**:
```bash
# Check API server logs
tail -f /path/to/api_server.log

# Look for errors like:
# ERROR: Quality metrics evaluation failed: ...
```

If you see errors in the quality evaluation:
- The error is caught and won't fail the query
- But metrics won't be recorded
- Check the error message for details

### Issue 2: Quality Metrics Show Null

**Symptom**: API response shows `"quality_metrics": null`

**Causes**:
1. No answer generated (empty response)
2. No sources retrieved
3. Evaluation code raised exception

**Solution**:
Check the API response:
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 3}' | jq '.'
```

Look for:
- `"answer": ""` (empty answer)
- `"sources": []` (no sources)
- `"quality_metrics": {"error": "..."}` (evaluation error)

### Issue 3: Grafana Shows "No Data"

**Symptoms**:
- Dashboard panels are empty
- Says "No data" or "N/A"

**Causes**:
1. No queries sent yet (no metrics collected)
2. Time range is wrong
3. Prometheus not scraping metrics
4. Dashboard queries are incorrect

**Solutions**:

**A. Send Test Queries**
```bash
# Send 5 test queries
for i in {1..5}; do
  curl -X POST http://localhost:8000/query \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"What is RAG pattern $i?\", \"top_k\": 3}"
  sleep 2
done
```

**B. Check Prometheus is Scraping**

1. Open Prometheus: http://localhost:9090
2. Go to "Status" > "Targets"
3. Find the target for `localhost:8000`
4. Should show "UP" with last scrape time

**C. Check Time Range**

1. In Grafana dashboard, click time picker (top right)
2. Select "Last 5 minutes" or "Last 15 minutes"
3. Click "Refresh"

**D. Test Prometheus Query**

1. Open Prometheus: http://localhost:9090
2. Enter query: `rag_answer_faithfulness_score`
3. Click "Execute"
4. Should show data points

If no data:
- Prometheus isn't scraping the metrics endpoint
- Check `docker-compose.yml` Prometheus configuration
- Check Prometheus is running: `docker-compose ps prometheus`

### Issue 4: Metrics Not in Prometheus Endpoint

**Symptom**: `curl http://localhost:8000/metrics` doesn't show quality metrics

**Causes**:
1. API server not restarted after code changes
2. Quality evaluation code has import errors
3. MetricsCollector not being called

**Solution**:

1. **Restart API server** (see Step 1 & 2 above)

2. **Check for import errors**:
```bash
cd semantic-pattern-query-app
python3 -c "from src.document_store.evaluation import evaluate_answer_quality, evaluate_context_quality; print('✅ Imports OK')"
```

If this fails, there's a problem with the evaluation module.

3. **Check MetricsCollector**:
```bash
python3 -c "from src.document_store.monitoring import MetricsCollector; print('✅ MetricsCollector OK')"
```

4. **Send a test query and check logs**:
```bash
# In one terminal, watch logs
tail -f /path/to/logs

# In another, send query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 3}'
```

Look for log messages like:
- `INFO: Hallucination detected ...` (if hallucination found)
- `ERROR: Quality metrics evaluation failed ...` (if error)

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] API server restarted after code changes
- [ ] Test query returns quality_metrics in response (not null)
- [ ] Prometheus metrics endpoint shows `rag_answer_*` metrics
- [ ] Prometheus targets show API server as "UP"
- [ ] Sent at least 3-5 test queries
- [ ] Grafana dashboard time range set to "Last 5-15 minutes"
- [ ] Dashboard panels show data (not "No data")

## Quick Fix Script

Create this script to restart everything:

```bash
#!/bin/bash
# restart_with_quality_metrics.sh

echo "Stopping API server..."
pkill -f api_server.py

echo "Waiting 3 seconds..."
sleep 3

echo "Starting API server..."
cd /Users/sanantha/SummarizerArchitecture/semantic-pattern-query-app
./venv/bin/python3 src/api_server.py &

echo "Waiting for server to start..."
sleep 5

echo "Sending test queries..."
for i in {1..5}; do
  echo "  Query $i/5..."
  curl -s -X POST http://localhost:8000/query \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"What is pattern $i?\", \"top_k\": 3}" > /dev/null
  sleep 2
done

echo ""
echo "✅ Done! Check Grafana dashboard:"
echo "   http://localhost:3333/d/4facbed2-cca8-4582-a2cc-c0e4b934a497/rag-quality-metrics"
```

Make it executable and run:
```bash
chmod +x restart_with_quality_metrics.sh
./restart_with_quality_metrics.sh
```

## Still Not Working?

If metrics still don't show after following all steps:

1. **Check the implementation is correct**:
   - Open [api_server.py](../src/api_server.py) in editor
   - Verify lines 191-267 have the quality evaluation code
   - Verify lines 29-30 have the imports

2. **Check for Python errors**:
   ```bash
   python3 src/api_server.py
   # Watch for any import errors or syntax errors
   ```

3. **Enable debug logging**:
   ```python
   # In api_server.py, line 31, change to:
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Test evaluation modules directly**:
   ```bash
   python3 test_quality_metrics_standalone.py
   ```

   If this works, the evaluation code is fine - the issue is in the API integration.

5. **Check Grafana dashboard queries**:
   - Open dashboard in edit mode
   - Check panel queries use correct metric names
   - Verify Prometheus datasource is configured

---

**Last Updated**: 2024-11-18
**Version**: 1.0
