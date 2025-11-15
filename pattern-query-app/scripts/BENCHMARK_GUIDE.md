# LLM Model Benchmark Guide

This guide explains how to benchmark different LLM models for the two-step schema generation and data extraction process.

## Available Benchmarks

### 1. Local Models (Ollama) - `benchmark_llm_models.py`

Tests local Ollama models for speed and quality.

**Models Tested:**
- `llama3.2:1b` - Very fast, lower quality
- `llama3.2:3b` - Fast, decent quality
- `qwen3:7b` - Medium speed, good quality
- `llama3.1:8b` - Medium speed, good quality
- `qwen3:14b` - Slower, better quality

**Requirements:**
- Ollama running on localhost:11434
- Models downloaded (`ollama pull <model>`)

**Usage:**
```bash
cd /Users/sanantha/SummarizerArchitecture/pattern-query-app

# Run benchmark
/Users/sanantha/SummarizerArchitecture/venv312/bin/python3 scripts/benchmark_llm_models.py
```

**What It Tests:**
1. **Schema Generation Time** - How long to create JSON schema
2. **Data Extraction Time** - How long to extract data with schema
3. **Quality Score** - Does it extract actual data (not schema)?
4. **Total Time** - Combined performance

**Output:**
```
BENCHMARK RESULTS - COMPARISON TABLE
================================================================================
Model                Size     Schema     Extract    Total      Quality    Status
--------------------------------------------------------------------------------
llama3.2:1b          1B       3.45s      2.31s      5.76s      6/10       ✅ PASS
qwen3:7b             7B       8.23s      6.12s      14.35s     9/10       ✅ PASS
qwen3:14b            14B      15.67s     12.34s     28.01s     10/10      ✅ PASS
--------------------------------------------------------------------------------

🏆 FASTEST: llama3.2:1b (5.76s total)
🏆 BEST QUALITY: qwen3:14b (score: 10/10)
🏆 BEST BALANCE: qwen3:7b
```

### 2. Cloud Models (Gemini, GPT) - `benchmark_cloud_llms.py`

Tests cloud LLM APIs for comparison with local models.

**Models Supported:**
- Google Gemini (gemini-2.0-flash-exp, gemini-1.5-pro)
- OpenAI GPT (add to script if needed)
- Anthropic Claude (add to script if needed)

**Requirements:**
- API keys set as environment variables

**Setup:**
```bash
# Set API keys
export GEMINI_API_KEY='your-api-key-here'
export OPENAI_API_KEY='your-api-key-here'  # Optional
```

**Usage:**
```bash
/Users/sanantha/SummarizerArchitecture/venv312/bin/python3 scripts/benchmark_cloud_llms.py
```

**What It Tests:**
1. Speed (latency)
2. Success rate
3. Estimated cost per operation

**Output:**
```
CLOUD LLM BENCHMARK RESULTS
================================================================================
Model                          Provider   Time       Cost         Status
--------------------------------------------------------------------------------
gemini-2.0-flash-exp           Google     1.23s      $0.000023    ✅ PASS
gemini-1.5-pro                 Google     2.45s      $0.000058    ✅ PASS
```

## Interpreting Results

### Speed Metrics

**Very Fast** (<5s total)
- Good for: Real-time applications, testing, development
- Models: llama3.2:1b, llama3.2:3b
- Trade-off: Lower quality

**Fast** (5-15s total)
- Good for: Production with reasonable latency
- Models: qwen3:7b, llama3.1:8b, Gemini Flash
- Trade-off: Good balance

**Slow** (15-30s total)
- Good for: Batch processing, offline tasks
- Models: qwen3:14b, llama3.1:70b
- Trade-off: Highest quality

**Very Slow** (>30s total)
- Good for: Critical accuracy tasks only
- Models: Large 70B+ models
- Trade-off: Very high quality, expensive

### Quality Scores

- **0-3**: Poor - Returns schema instead of data, or very incomplete
- **4-6**: Fair - Extracts some data but misses content
- **7-8**: Good - Most data extracted correctly
- **9-10**: Excellent - Complete and accurate extraction

### Recommendations by Use Case

#### Development/Testing
**Best Choice:** `llama3.2:1b` or `llama3.2:3b`
- Reason: Fast iteration, immediate feedback
- Speed: <6s
- Quality: Sufficient for testing

#### Production (Real-time)
**Best Choice:** `qwen3:7b` or `gemini-2.0-flash-exp`
- Reason: Good balance of speed and quality
- Speed: 5-15s
- Quality: Good (7-8/10)

#### Production (Batch)
**Best Choice:** `qwen3:14b`
- Reason: Best quality for offline processing
- Speed: Not critical (15-30s ok)
- Quality: Excellent (9-10/10)

#### Production (Cloud)
**Best Choice:** `gemini-2.0-flash-exp`
- Reason: Very fast, very cheap, good quality
- Speed: 1-2s
- Cost: ~$0.00002 per operation
- Quality: Good

## Cost Comparison

### Local Models (Ollama)
- **Cost:** $0 (free)
- **Setup:** Requires local hardware
- **Latency:** Depends on hardware (5-30s typical)

### Cloud Models
- **Gemini Flash:** ~$0.00002 per operation
- **Gemini Pro:** ~$0.00005 per operation
- **GPT-4 Turbo:** ~$0.0002 per operation

**Example:** 1000 operations/day
- Local (free): $0/month
- Gemini Flash: $0.60/month
- GPT-4 Turbo: $6.00/month

## Customizing Benchmarks

### Add More Local Models

Edit `benchmark_llm_models.py`:
```python
MODELS_TO_TEST = [
    {"name": "llama3.2:1b", "size": "1B", "expected_speed": "very fast"},
    {"name": "your-model:tag", "size": "XB", "expected_speed": "fast"},  # Add here
]
```

### Add More Cloud Models

Edit `benchmark_cloud_llms.py`:
```python
CLOUD_MODELS = [
    {
        "name": "gpt-4-turbo",
        "provider": "OpenAI",
        "cost_per_1k_tokens": 0.01,
        "use_ollama": False,
        "requires_api_key": "OPENAI_API_KEY"
    },
]
```

### Change Test Content

Edit the `TEST_CONTENT` variable in either script to use your own sample data.

## Troubleshooting

### "Model not found"
```bash
# Download the model first
ollama pull llama3.2:1b
```

### "API key not set"
```bash
# Set the environment variable
export GEMINI_API_KEY='your-key'
```

### "Connection error"
```bash
# Check Ollama is running
ollama list

# Restart Ollama if needed
```

### "Out of memory"
Skip larger models or reduce batch size in your system.

## Next Steps

1. **Run Ollama Benchmark:**
   ```bash
   python3 scripts/benchmark_llm_models.py
   ```

2. **Review Results:**
   - Check `benchmark_results.json` for detailed data

3. **Choose Model:**
   - Development: Use fastest model
   - Production: Use best balance model
   - Critical: Use highest quality model

4. **Update Configuration:**
   ```bash
   # In .env
   OLLAMA_MODEL=qwen3:7b  # Your chosen model
   ```

5. **Test in ADK:**
   ```bash
   cd .adk/agents
   OLLAMA_MODEL=qwen3:7b adk web --port=8090
   ```
