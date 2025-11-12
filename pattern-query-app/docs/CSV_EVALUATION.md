# CSV Formatting Evaluation Guide

**Date:** 2025-11-12
**Purpose:** Evaluate LLM model capabilities for generating properly formatted CSV output

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Detailed Workflow](#detailed-workflow)
4. [Validation Criteria](#validation-criteria)
5. [Current Results](#current-results)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This evaluation system tests whether different LLM models can successfully:
1. Retrieve complete documents from ChromaDB vector store
2. Format large tables (163 rows, 7 columns) as properly structured CSV
3. Apply correct CSV quoting rules for fields with commas, quotes, and special characters
4. Generate output ready for Google Sheets import

### Why This Matters

**Problem:** Not all LLM models can follow complex formatting instructions. Smaller models (like qwen3:14b) may return markdown outlines or improperly formatted data instead of valid CSV.

**Solution:** This evaluation system provides:
- Standardized test case with clear validation criteria
- Automated CSV validation (structure, row/column counts, quoting)
- Multi-model comparison framework
- Clear pass/fail metrics

---

## Quick Start

### Prerequisites

1. **Ollama installed and running**: `ollama list` should show available models
2. **Python 3.9+**: With required dependencies installed
3. **Vector store populated**: Run `python scripts/ingest_all_docs.py` first
4. **Models downloaded**: Download models you want to test via Ollama

### 30-Second Validation

Test an existing agent response:

```bash
python3 scripts/run_simple_eval.py \
  --eval-file csv_format_eval_set.json \
  --validate-response /path/to/agent_response.txt
```

**Expected Output:**
```
Validation Results for: /path/to/agent_response.txt
============================================================
Valid: True
Metrics: {
  "row_count": 163,
  "column_count": 7,
  "header": ["Phase", "Category", "Technique/Methodology", ...],
  "none_count": 0
}
```

---

## Detailed Workflow

### Step 1: Configure Model Under Test

Edit `.env` file:

```bash
# Change this line to the model you want to test
OLLAMA_MODEL=gemma2:27b

# Default Ollama base URL (usually doesn't need to change)
OLLAMA_BASE_URL=http://localhost:11434/v1
```

**Available Models** (download with `ollama pull <model>`):
- `qwen3:14b` - 14B parameter Qwen model (already tested: FAIL)
- `gemma2:27b` - 27B parameter Google Gemma 2
- `llama3.1:70b` - 70B parameter Meta Llama 3.1 (strongest option)
- `mistral:latest` - Mistral AI's latest model
- `mixtral:8x7b` - Mixtral MoE model

### Step 2: Start Ollama Agent

**Option A: Using startup script** (Recommended):
```bash
cd /Users/sanantha/SummarizerArchitecture/pattern-query-app
./scripts/start_adk_ollama.sh
```

**Option B: Manual start**:
```bash
cd /Users/sanantha/SummarizerArchitecture/pattern-query-app
export OLLAMA_MODEL=gemma2:27b
export OLLAMA_BASE_URL=http://localhost:11434/v1
../venv312/bin/adk web --host=127.0.0.1 --port=8000 --allow_origins="*" .adk/agents
```

**Verify Agent Started:**
- Terminal shows: `INFO:     Uvicorn running on http://127.0.0.1:8000`
- Open http://127.0.0.1:8000 in browser
- You should see the ADK web interface

### Step 3: Run Test Query

1. **Open Web UI**: http://127.0.0.1:8000
2. **Select Agent**: Choose `ollama_agent` from dropdown
3. **Enter Test Query** (copy-paste this exact text):
   ```
   list the 'Complete Techniques Catalog' as csv that i can copy paste into google sheet
   ```
4. **Wait for Response**: Agent will retrieve document and format as CSV (5-15 seconds)

### Step 4: Save Agent Response

**Important:** Save the COMPLETE response, including any explanation text before the CSV.

1. **Copy Full Response**: Select all text in agent response (Cmd+A / Ctrl+A)
2. **Save to File**:
   ```bash
   # Create test directory if it doesn't exist
   mkdir -p /Users/sanantha/SummarizerArchitecture/test

   # Save response (replace <model> with actual model name)
   # Example filename: llm_response_gemma2_27b.txt
   # Use underscores to replace colons in model names
   ```
3. **File Naming Convention**:
   - Pattern: `llm_response_<model_name>.txt`
   - Replace `:` with `_` in model names
   - Examples:
     - `llm_response_qwen3_14b.txt`
     - `llm_response_gemma2_27b.txt`
     - `llm_response_llama3.1_70b.txt`
     - `llm_response_mixtral_8x7b.txt`

### Step 5: Validate Response

Run validation script:

```bash
python3 scripts/run_simple_eval.py \
  --eval-file csv_format_eval_set.json \
  --validate-response /Users/sanantha/SummarizerArchitecture/test/llm_response_gemma2_27b.txt
```

**Successful Validation Output:**
```
Validation Results for: /Users/sanantha/SummarizerArchitecture/test/llm_response_gemma2_27b.txt
============================================================
Valid: True
Metrics: {
  "row_count": 163,
  "column_count": 7,
  "header": [
    "Phase",
    "Category",
    "Technique/Methodology",
    "Description",
    "Process Framework",
    "Usage in Architecture",
    "Lifecycle Steps"
  ],
  "none_count": 0
}
```

**Failed Validation Output:**
```
Validation Results for: /Users/sanantha/SummarizerArchitecture/test/llm_response_qwen3_14b.txt
============================================================
Valid: False
Metrics: {
  "row_count": 35,
  "column_count": 8,
  "header": [...],
  "none_count": 202
}
Errors:
  - Row count 35 below minimum 160
  - Column count 8 != expected 7
  - Found 202 None or empty columns
```

### Step 6: Repeat for Additional Models

1. Stop current agent (Ctrl+C in terminal)
2. Edit `.env` - change `OLLAMA_MODEL=<next_model>`
3. Restart agent: `./scripts/start_adk_ollama.sh`
4. Run test query in web UI
5. Save response with new filename
6. Validate response

---

## Validation Criteria

### Structural Requirements

**From `csv_format_eval_set.json` test case:**

| Criteria | Expected Value | Description |
|----------|----------------|-------------|
| **Row Count** | 163 rows | Data rows (excluding header) |
| **Row Range** | 160-165 | Acceptable range (allows minor variations) |
| **Column Count** | 7 columns | Exact match required |
| **Header Row** | Present | Must have header with column names |
| **None Columns** | 0 | No None or empty columns allowed |

### Column Names (Exact Order)

1. Phase
2. Category
3. Technique/Methodology
4. Description
5. Process Framework
6. Usage in Architecture
7. Lifecycle Steps

### CSV Formatting Rules

**Quoting Requirements:**
- ✅ All fields with commas MUST be quoted
- ✅ All fields with double quotes MUST be quoted (and internal quotes escaped)
- ✅ All fields with newlines MUST be quoted
- ✅ Markdown formatting (**, *, etc.) must be stripped

**Examples of Proper Formatting:**
```csv
"1. Ideation & Planning","Data Analysis","Exploratory Data Analysis (EDA)","Initial data exploration to understand patterns, distributions, and relationships","CRISP-DM, KDD Process","Analyze data (FHIR, EHR, BigQuery)","1.1, 3.1"
```

**Common Errors to Avoid:**
```csv
# ❌ WRONG - Commas not quoted
1. Ideation & Planning,Data Analysis,EDA,Initial data exploration to understand patterns, distributions, and relationships,CRISP-DM, KDD Process,...

# ❌ WRONG - Field splitting
"1. Ideation & Planning","Data Analysis","EDA","Initial data exploration to understand patterns"," distributions"," and relationships",...

# ✅ CORRECT - All commas properly quoted
"1. Ideation & Planning","Data Analysis","EDA","Initial data exploration to understand patterns, distributions, and relationships","CRISP-DM, KDD Process",...
```

### Validation Script Logic

The validator (`scripts/run_simple_eval.py::validate_csv_format()`):

1. **Finds CSV Start**: Scans response for header row (looks for line with 6+ commas)
2. **Parses CSV**: Uses Python's `csv.DictReader` to parse content
3. **Counts Rows**: Verifies row count in range 160-165
4. **Counts Columns**: Verifies exactly 7 columns
5. **Checks None Values**: Counts any None or empty columns (must be 0)
6. **Verifies Header**: Confirms header row exists

---

## Current Results

### Tested Models

| Model | Status | Row Count | Column Count | None Count | Notes |
|-------|--------|-----------|--------------|------------|-------|
| **gemini-2.0-flash-exp** | ✅ PASS | 163 | 7 | 0 | Perfect CSV formatting |
| **qwen3:14b** | ❌ FAIL | 35 | 8 | 202 | Returns markdown outline |
| **mannix/deepseek-coder-v2-lite-instruct:q8_0** | ❌ FAIL | 10 | 3 | 2 | Partial response, incorrect formatting |
| **granite4:latest** | ❌ FAIL | 0 | 1 | 0 | No valid CSV output, empty or error response |
| **gemma3:4b-it-qat** | ❌ FAIL | 36 | - | 145 | Partial response with many empty columns |
| **gpt-oss:latest** | ❌ FAIL | 13 | 9 | - | Partial response, wrong column count |
| **gemma2:27b** | ⚠️ NOT TESTED | - | - | - | Ready for testing |
| **llama3.1:70b** | ⚠️ NOT TESTED | - | - | - | Ready for testing |
| **mistral:latest** | ⚠️ NOT TESTED | - | - | - | Ready for testing |

### Analysis

**Why Gemini Passes:**
- Strong instruction-following capability
- Handles complex formatting requirements
- Properly applies CSV quoting rules
- Understands "copy-paste into Google Sheets" requirement

**Why Qwen3:14b Fails:**
- Smaller 14B model with weaker instruction-following
- Defaults to markdown hierarchical outline format
- Ignores CSV formatting instructions in prompt
- Cannot handle complex multi-step formatting task

**Why Deepseek-Coder-v2-lite-instruct:q8_0 Fails:**
- Code-focused model (not optimized for data formatting tasks)
- Returns only 10 rows instead of 163 (partial response)
- Wrong column structure (3 columns instead of 7)
- May have context window limitations or truncation issues
- Response length: 1497 characters (too short for complete table)

**Why Granite4:latest Fails:**
- Returns 0 rows, 1 column (no valid CSV output)
- May have failed to parse the markdown table input
- Could be context window limitations or model incompatibility
- Response may be empty or error message instead of CSV

**Why Gemma3:4b-it-qat Fails:**
- Very small 4B model with limited capacity
- Returns only 36 rows instead of 163 (partial response)
- 145 empty/None columns (incorrect CSV structure)
- Context window or processing limitations for large tables
- Response time: 77.95s (slower than other models)

**Why GPT-OSS:latest Fails:**
- Returns only 13 rows instead of 163 (severe truncation)
- Wrong column count: 9 instead of 7 (incorrect structure)
- May have context window limitations or processing issues
- Response time: 108.90s (slowest tested model)
- Likely truncation or incomplete processing of large table

**Expected Results:**
- **Gemma2:27b**: Likely to PASS (27B, Google-trained on instruction-following)
- **Llama3.1:70b**: Very likely to PASS (70B, strongest open-source model)
- **Mistral:latest**: Moderate chance to PASS (strong instruction-following)

---

## Troubleshooting

### Issue: Agent doesn't respond

**Symptoms:**
- Web UI shows "Generating..." indefinitely
- Terminal shows errors about model not found

**Solutions:**
1. **Verify model is downloaded**:
   ```bash
   ollama list  # Should show your model
   ollama pull gemma2:27b  # Download if missing
   ```

2. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/v1/models  # Should return JSON
   ```

3. **Check .env configuration**:
   ```bash
   cat .env | grep OLLAMA_MODEL  # Should match ollama list
   ```

### Issue: Validation fails with "FileNotFoundError"

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'test/llm_response.txt'
```

**Solutions:**
1. **Use absolute path**:
   ```bash
   python3 scripts/run_simple_eval.py \
     --validate-response /Users/sanantha/SummarizerArchitecture/test/llm_response_gemma2_27b.txt
   ```

2. **Verify file exists**:
   ```bash
   ls -lh /Users/sanantha/SummarizerArchitecture/test/*.txt
   ```

### Issue: CSV validation fails but output looks correct

**Symptoms:**
- Visual inspection shows CSV looks correct
- Validation reports wrong row/column counts

**Solutions:**
1. **Check for extra blank lines**: Remove trailing newlines
2. **Check for markdown formatting**: Ensure agent didn't include explanation after CSV
3. **Manual CSV parse test**:
   ```python
   import csv
   with open('llm_response.txt') as f:
       reader = csv.DictReader(f)
       rows = list(reader)
       print(f"Rows: {len(rows)}, Columns: {len(reader.fieldnames)}")
   ```

### Issue: Agent returns partial response

**Symptoms:**
- Agent response stops mid-table
- Row count is too low (e.g., 50 instead of 163)

**Solutions:**
1. **Check model context window**: Smaller models may have shorter context
2. **Verify complete document retrieval**: Check terminal logs for ChromaDB errors
3. **Try larger model**: Use llama3.1:70b or gemma2:27b instead

### Issue: Import to Google Sheets creates wrong columns

**Symptoms:**
- Fields with commas get split into multiple columns
- "Process Framework" shows " distributions" instead of "CRISP-DM, KDD Process"

**Solutions:**
1. **Validation should catch this**: Run validation first before importing
2. **Check quoting**: All fields with commas must be in double quotes
3. **Use different model**: Current model failed to follow CSV formatting rules

---

## Advanced: Multi-Model Comparison

Generate test plan for multiple models at once:

```bash
python3 scripts/run_simple_eval.py \
  --eval-type csv \
  --eval-file csv_format_eval_set.json \
  --models qwen3:14b,gemma2:27b,llama3.1:70b,mistral:latest
```

**Output:**
- Prints testing instructions for each model
- Saves test plan to `csv_eval_results.json`
- You still need to manually run each model and validate

**Workflow:**
1. Run command above to generate test plan
2. For each model listed:
   - Configure model in `.env`
   - Start agent
   - Run query
   - Save response
   - Validate response
3. Compare results across models

---

## Files Reference

### Evaluation Files

- **Test Case**: `csv_format_eval_set.json` - Test definition with validation criteria
- **Validation Script**: `scripts/run_simple_eval.py` - CSV validation and multi-model testing
- **Configuration**: `.env` - Model configuration
- **Responses**: `test/llm_response_*.txt` - Saved agent responses

### Documentation Files

- **This Guide**: `docs/CSV_EVALUATION.md` - Comprehensive evaluation documentation
- **README**: `README.md` - Quick start guide in main README
- **Final Status**: `docs/FINAL_STATUS.md` - Overall project status (includes CSV work)
- **Validation Report**: `docs/VALIDATION_REPORT.md` - Gemini agent validation results

---

## Command Reference

### Validation Commands

```bash
# Validate single response
python3 scripts/run_simple_eval.py \
  --eval-file csv_format_eval_set.json \
  --validate-response /path/to/response.txt

# Generate multi-model test plan
python3 scripts/run_simple_eval.py \
  --eval-type csv \
  --eval-file csv_format_eval_set.json \
  --models qwen3:14b,gemma2:27b,llama3.1:70b

# Standard RAG evaluation (different test)
python3 scripts/run_simple_eval.py \
  --eval-file simple_eval_set.json
```

### Agent Commands

```bash
# Start Ollama agent (reads OLLAMA_MODEL from .env)
./scripts/start_adk_ollama.sh

# Start Gemini agent
./scripts/start_adk_gemini.sh

# Verify Ollama models
ollama list

# Download new model
ollama pull gemma2:27b
```

### File Management

```bash
# Create test directory
mkdir -p /Users/sanantha/SummarizerArchitecture/test

# List saved responses
ls -lh /Users/sanantha/SummarizerArchitecture/test/*.txt

# View response file
cat /Users/sanantha/SummarizerArchitecture/test/llm_response_gemma2_27b.txt
```

---

## Next Steps

1. **Test Gemma2:27b**:
   - Expected to PASS (strong 27B model)
   - Good balance of quality and speed

2. **Test Llama3.1:70b**:
   - Expected to PASS (strongest open-source model)
   - Slower but highest quality

3. **Document Results**:
   - Update this guide with actual results
   - Add model recommendations based on performance

4. **Production Recommendation**:
   - Use Gemini for production (proven to work)
   - Use Gemma2:27b or Llama3.1:70b as local alternative if they pass

---

## Support

**Questions or Issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review terminal logs for error messages
- Verify model is downloaded: `ollama list`
- Ensure vector store is populated: `python -c "from src.document_store.storage.vector_store import VectorStore; vs = VectorStore(); print(vs.get_collection_info())"`

**Related Documentation:**
- [README.md](../README.md) - Main project documentation
- [FINAL_STATUS.md](FINAL_STATUS.md) - Overall status including CSV implementation
- [VALIDATION_REPORT.md](VALIDATION_REPORT.md) - Detailed validation results
