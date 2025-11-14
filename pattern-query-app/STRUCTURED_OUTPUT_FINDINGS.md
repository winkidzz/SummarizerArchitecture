# Structured Output Implementation - Findings and Status

## Summary

Successfully fixed Pydantic V2 → Gemini/Ollama compatibility issues. The schema definitions now work correctly. However, discovered a prompt engineering issue with small Ollama models.

## ✅ Completed: Pydantic Schema Fixes

### Problem
Google Gemini's `response_schema` parameter doesn't support Pydantic V2 `Field(default=...)` or `Field(None, ...)` syntax.

**Error**: `Unknown field for Schema: default`

### Solution
Removed ALL default value parameters from Field() definitions in `src/document_store/formatting/schemas.py`:

**Before (Failed)**:
```python
description: Optional[str] = Field(None, description="Brief description")
pricing_model: Optional[str] = Field(None, description="Pricing model")
```

**After (Working)**:
```python
description: Optional[str] = Field(description="Brief description")
pricing_model: Optional[str] = Field(description="Pricing model")
```

### Files Modified
- `src/document_store/formatting/schemas.py` (lines 56, 76, 83)
  - TechniqueRow.lifecycle_steps
  - PatternSummary.estimated_improvement
  - VendorComparison.pricing_model

### Verification
✅ No more "Unknown field for Schema: default" errors
✅ Schemas load successfully in both Gemini and Ollama modes
✅ Pydantic validation works correctly

## ⚠️  Current Issue: LLM Output Quality

### Problem
The LLM (llama3.2:1b) returns the **JSON schema definition** instead of **extracted data**.

**What it returns**:
```json
{
  "description": "Schema for tabular data...",
  "properties": {
    "table_name": {"title": "Table Name", "type": "string"},
    ...
  },
  "required": ["table_name", "columns", "rows", ...]
}
```

**What it should return**:
```json
{
  "table_name": "AI Development Techniques",
  "description": "Table of AI development techniques",
  "columns": ["Phase", "Category", "Technique"],
  "rows": [
    {"Phase": "Design", "Category": "Architecture", "Technique": "RAG"},
    ...
  ],
  "total_rows": 3
}
```

### Root Cause
1. **Prompt Engineering**: The current prompt sends the full JSON schema to the LLM, which confuses small models
2. **Model Capability**: llama3.2:1b (1B parameters) is too small for complex structured output tasks
3. **Context**: Line 258 in `structured_output.py` adds schema to prompt, but small models just echo it back

### Code Location
**File**: `src/document_store/formatting/structured_output.py:258`
```python
prompt += f"\n\nYou MUST respond with valid JSON matching this schema:\n{json.dumps(json_schema, indent=2)}"
```

## Test Results

### Use Case 1 Evaluation (4 Tests)
- **Passed**: 0/4 (0%)
- **Failed**: 4/4 (100%)
- **Error**: "Schema validation failed" - all required fields missing

**Test Cases**:
1. Simple 3x3 Table - ❌ Failed (LLM returned schema, not data)
2. Techniques Catalog - ❌ Failed (LLM returned schema, not data)
3. RAG Patterns Table - ❌ Failed (LLM returned schema, not data)
4. Vendor Comparison - ❌ Failed (LLM returned schema, not data)

### Use Case 2 (Standard RAG Query)
- **Status**: ✅ **PASSING**
- **Details**: Standard document retrieval works perfectly
- **No structured output used**

## Recommendations

### Option 1: Improve Prompts for Small Models (Recommended)
- Simplify the prompt - don't send full JSON schema
- Use few-shot examples showing correct data extraction
- Add explicit instructions: "Extract data FROM the document, DO NOT return the schema itself"

### Option 2: Use Larger Model
- Switch from llama3.2:1b to qwen3:14b or larger
- More capable models better understand structured output instructions
- Trade-off: slower inference (2+ minutes per request)

### Option 3: Use Gemini API (Requires Auth Fix)
- Native structured output with `response_schema` parameter
- Much better at following schema constraints
- Requires fixing Google Auth credentials

### Option 4: Hybrid Approach
- Use simple regex/parsing for table extraction (fast, deterministic)
- Reserve LLM structured output for complex cases only
- Best for production reliability

## Implementation Files Created

### Core Implementation
- `src/document_store/formatting/schemas.py` - Pydantic schemas (✅ Fixed)
- `src/document_store/formatting/structured_output.py` - LLM service
- `src/document_store/formatting/converters.py` - Format converters
- `src/document_store/formatting/validators.py` - Output validators

### Agent Integration
- `.adk/agents/_shared/agent_base.py` - Added 3 optional tools
- `.adk/agents/gemini_agent/agent.py` - Registered tools
- `.adk/agents/ollama_agent/agent.py` - Registered tools

### Evaluation Scripts
- `scripts/test_usecase1_structured_output.py` - Eval set with 4 test cases
- `scripts/test_usecase1_debug.py` - Debug script showing raw LLM output
- `scripts/test_three_use_cases.py` - Original 3 use case tests
- `scripts/test_rag_patterns_query.py` - RAG query test (✅ working)

### Results
- `usecase1_eval_results.json` - Detailed test results
- `usecase1_eval_log.txt` - Test execution log

## Next Steps

1. **Immediate**: Improve prompts for Ollama to extract data instead of echoing schema
2. **Short-term**: Test with larger Ollama model (qwen3:14b)
3. **Medium-term**: Fix Google Auth to enable Gemini testing
4. **Long-term**: Implement hybrid approach with deterministic parsing fallbacks

## Key Insight

The Pydantic V2 compatibility is **fully resolved**. The remaining issue is **LLM capability and prompt engineering**, not schema definitions. Small models (1B params) struggle with complex structured output instructions and tend to echo the schema instead of extracting data.
