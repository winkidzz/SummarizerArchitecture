# Evaluation Configuration Guide

This document explains how to configure the RAG evaluation system using environment variables.

## Environment Variables

Configure evaluation behavior in the `.env` file:

```bash
# RAG Evaluation Configuration
# Use Ollama (true) or Gemini (false) for evaluation judge
USE_OLLAMA_EVAL=false

# Use Real Ragas library (true) or Custom implementation (false)
USE_REAL_RAGAS=false

# CSV Formatting Evaluation Configuration (NEW - 2025-11-12)
# Ollama model to use for ADK agents
OLLAMA_MODEL=qwen3:14b

# Ollama base URL
OLLAMA_BASE_URL=http://localhost:11434/v1

# Gemini model for ADK agents
GEMINI_MODEL=gemini-2.5-flash
ADK_MODEL=gemini-2.5-flash
```

## Configuration Matrix

| USE_OLLAMA_EVAL | USE_REAL_RAGAS | Evaluator Used | Speed | Status |
|-----------------|----------------|----------------|-------|--------|
| `false` | `false` | **Custom Gemini** (recommended) | Fast (3-4s/case) | ✅ Working |
| `false` | `true` | Real Ragas + Gemini | Fast (expected) | ⚠️ Dependency issues |
| `true` | `false` | Custom Ollama | Slow (80-160s/case) | ✅ Working (slow) |
| `true` | `true` | N/A | N/A | ❌ Not implemented |

## Recommended Configuration

**For production/reliable evaluation:**
```bash
USE_OLLAMA_EVAL=false  # Use Gemini API
USE_REAL_RAGAS=false   # Use custom implementation
```

This configuration:
- Uses the custom Gemini evaluator
- Very fast (3-4 seconds per test case)
- Reliable score parsing
- No dependency conflicts
- Requires `GEMINI_API_KEY` in `.env`

## Alternative Configurations

### Using Local Ollama (Slower but Free)

```bash
USE_OLLAMA_EVAL=true   # Use local Ollama
USE_REAL_RAGAS=false   # Use custom implementation
```

Requirements:
- Ollama server running at `http://192.168.1.204:11434` (or configure with `--ollama-url`)
- Model available (default: `qwen3:14b`)
- Much slower: 80-160 seconds per test case
- May have score parsing issues with smaller models

### Using Real Ragas Library (Experimental)

```bash
USE_OLLAMA_EVAL=false  # Use Gemini API
USE_REAL_RAGAS=true    # Use official Ragas library
```

Status: ⚠️ **Currently has dependency conflicts**

Issue:
- `langchain-google-genai` version compatibility
- Error: `module 'langchain' has no attribute 'verbose'`

To attempt fix (may break other packages):
```bash
pip install --upgrade google-generativeai langchain-google-genai
```

## Running Evaluations

### Basic Usage

```bash
# With default configuration from .env
python scripts/run_ragas_eval.py --eval-file ragas_eval_set_quick.json

# With full evaluation set
python scripts/run_ragas_eval.py --eval-file ragas_eval_set.json

# Specify output file
python scripts/run_ragas_eval.py --eval-file ragas_eval_set_quick.json --output results.json
```

### Overriding Model

```bash
# Use different Gemini model
python scripts/run_ragas_eval.py --model gemini-1.5-pro

# Use different Ollama model (when USE_OLLAMA_EVAL=true)
python scripts/run_ragas_eval.py --model llama3.1:latest
```

## Evaluation Metrics

The system computes 4 Ragas-style metrics:

1. **Faithfulness** (0-1): Is the response grounded in retrieved documents?
2. **Answer Relevancy** (0-1): Does the response answer the query?
3. **Context Precision** (0-1): Are retrieved documents relevant to the query?
4. **Context Recall** (0-1): Were all necessary documents retrieved?

**Overall Score**: Average of the 4 metrics

## Evaluation Datasets

### RAG Evaluation Test Sets

- `simple_eval_set.json` - 5 fast vector retrieval tests (~82ms per query)
- `ragas_eval_set_quick.json` - 2 quick Ragas evaluation tests (recommended for testing)
- `ragas_eval_set.json` - 5 standard Ragas tests
- `ragas_eval_set_complex.json` - 8 complex tests (CSV formatting, multi-hop reasoning)

### CSV Formatting Evaluation (NEW - 2025-11-12)

Test LLM model capabilities for generating properly formatted CSV output.

**Test Set:**
- `csv_format_eval_set.json` - CSV formatting validation test
  - Query: "list the 'Complete Techniques Catalog' as csv..."
  - Expected: 163 rows, 7 columns, proper CSV structure
  - Validates: row count, column count, quoting rules, header

**Usage:**
```bash
# Validate an existing agent response
python3 scripts/run_simple_eval.py \
  --eval-file csv_format_eval_set.json \
  --validate-response /path/to/response.txt

# Generate test plan for multiple Ollama models
python3 scripts/run_simple_eval.py \
  --eval-type csv \
  --eval-file csv_format_eval_set.json \
  --models qwen3:14b,gemma2:27b,llama3.1:70b
```

**Manual Testing Required:**
CSV evaluation requires manual agent interaction. See [docs/CSV_EVALUATION.md](docs/CSV_EVALUATION.md) for complete workflow:
1. Configure model in `.env`
2. Start agent
3. Run test query
4. Save response
5. Validate with script

**Current Results:**
| Model | Status | Notes |
|-------|--------|-------|
| gemini-2.5-flash | ✅ PASS | Perfect CSV formatting (163 rows, 7 columns) |
| gemini-2.0-flash-exp | ✅ PASS | Perfect CSV formatting (163 rows, 7 columns) |
| qwen3:14b | ❌ FAIL | Returns markdown outline (35 rows, 8 columns) |
| mannix/deepseek-coder-v2-lite-instruct:q8_0 | ❌ FAIL | Partial response (10 rows, 3 columns) |
| granite4:latest | ❌ FAIL | No valid CSV output (0 rows, 1 column) |
| gemma3:4b-it-qat | ❌ FAIL | Partial response (36 rows, many empty columns) |
| gpt-oss:latest | ❌ FAIL | Severe truncation (13 rows, 9 columns) |
| gemma2:27b | ⚠️ NOT TESTED | Ready to test |
| llama3.1:70b | ⚠️ NOT TESTED | Ready to test |

📖 **Full Guide**: [docs/CSV_EVALUATION.md](docs/CSV_EVALUATION.md)

## Troubleshooting

### Custom Gemini Evaluator Not Working

Error: `Failed to initialize Gemini evaluator`

Solution:
1. Check `GEMINI_API_KEY` is set in `.env`
2. Verify API key is valid: https://aistudio.google.com/app/apikey
3. Install required package: `pip install google-generativeai`

### Ollama Timeout Issues

Error: `Operation timed out`

Solutions:
1. Verify Ollama server is running: `curl http://192.168.1.204:11434/api/tags`
2. Use smaller test set: `ragas_eval_set_quick.json`
3. Increase timeout (already 5 minutes)
4. Switch to Gemini: Set `USE_OLLAMA_EVAL=false`

### Real Ragas Import Errors

Error: `Ragas is not installed` or `module 'langchain' has no attribute 'verbose'`

Solution:
- Set `USE_REAL_RAGAS=false` to use stable custom implementation
- OR attempt to fix dependencies (may break other packages)

## Performance Comparison

| Evaluator | Speed (per case) | Reliability | Setup |
|-----------|------------------|-------------|-------|
| Custom Gemini | **3-4s** | ✅ High | API key only |
| Real Ragas + Gemini | ~5s (expected) | ⚠️ Dependency issues | Complex setup |
| Custom Ollama | 80-160s | ⚠️ Parsing issues | Local server |

## No Fallback Logic

The system will **fail explicitly** if the configured evaluator cannot be initialized. This prevents confusion from silent fallbacks:

- If `USE_REAL_RAGAS=true` but Real Ragas fails → **Error** (no fallback to custom)
- If `USE_OLLAMA_EVAL=true` but Ollama unavailable → **Error** (no fallback to Gemini)

To change evaluator, explicitly update `.env` configuration.
