# Structured Output Feature

## Overview

The Pattern Query App now includes **LLM-driven adaptive structured output** generation. This feature allows the AI agent to intelligently decide when to generate structured data (tables, lists, comparisons) vs free-form text, based on user query intent.

## Key Concept

**The LLM decides when structured output is appropriate** - not every query needs structured output!

- **Conceptual queries** → Free-form markdown text (default behavior)
- **Data queries** → Structured output with schema validation

## Architecture

### Flow

```
User Query
    ↓
Agent analyzes query intent
    ↓
Decision Point:
├─→ Conceptual/Explanatory → Use standard tools (query_architecture_patterns)
└─→ Tabular/Structured data → Use structured output tools
         ↓
    Retrieve document content
         ↓
    LLM extracts structured data + generates schema-compliant JSON
         ↓
    Validate JSON against Pydantic schema
         ↓
    Convert JSON → Requested format (CSV, Markdown, HTML, etc.)
         ↓
    Return validated output
```

### Components

1. **Schema Registry** (`src/document_store/formatting/schemas.py`)
   - Defines Pydantic schemas for common data structures
   - Generic schemas: `TableSchema`, `ListSchema`, `ComparisonSchema`
   - Specialized schemas: `TechniquesCatalog`, `PatternSummary`, `VendorComparison`
   - Auto-inference based on content and query

2. **Structured Output Service** (`src/document_store/formatting/structured_output.py`)
   - LLM integration (Gemini native structured output, Ollama JSON mode)
   - Schema-based generation with validation
   - Error handling and fallback logic

3. **Format Converters** (`src/document_store/formatting/converters.py`)
   - JSON → CSV, TSV, Markdown, HTML, YAML
   - Preserves data integrity
   - Proper escaping and formatting

4. **Output Validators** (`src/document_store/formatting/validators.py`)
   - Schema validation via Pydantic
   - Content completeness checks
   - Format-specific validation (CSV structure, etc.)

5. **Agent Tools** (`.adk/agents/_shared/agent_base.py`)
   - `generate_structured_table()`: For tabular data extraction
   - `generate_structured_list()`: For list/catalog extraction
   - `generate_comparison_matrix()`: For comparison matrices

## When to Use Structured Output

### Agent Decision Logic

The agent **automatically decides** based on query patterns:

#### Use Structured Output Tools When:

1. **User explicitly requests structured format**
   - "List as CSV"
   - "Create a table"
   - "Show in spreadsheet format"
   - "Generate a comparison matrix"

2. **Query implies structured data**
   - "Compare X vs Y" → `generate_comparison_matrix()`
   - "List all X" → `generate_structured_list()`
   - "Catalog of Y" → `generate_structured_table()`

3. **Output needs schema validation**
   - Large tables with many rows/columns
   - Data that will be processed programmatically
   - Exports to other systems

#### Do NOT Use Structured Output Tools When:

1. **Conceptual questions**
   - "How does RAG work?"
   - "Explain contextual retrieval"
   - "What are the benefits of...?"

2. **General queries**
   - "Tell me about Anthropic"
   - "What patterns are available?"
   - Single item lookups

3. **No specific format requested**
   - Use standard `query_architecture_patterns()` or `get_complete_document()`

## Example Queries

### Structured Output Examples

```
Query: "List the Complete Techniques Catalog as CSV"
Tool: generate_structured_table(source_filter='ai-development-techniques', output_format='csv')
Output: Valid CSV with schema validation
```

```
Query: "Compare Anthropic vs Azure OpenAI features"
Tool: generate_comparison_matrix(entities='Anthropic, Azure OpenAI', dimensions='features')
Output: Comparison matrix (markdown/CSV/HTML)
```

```
Query: "List all RAG patterns with their complexity"
Tool: generate_structured_list(query='RAG patterns complexity', output_format='json')
Output: Structured JSON list with validation
```

### Non-Structured Examples (Standard Tools)

```
Query: "Explain how contextual retrieval works"
Tool: query_architecture_patterns(query='contextual retrieval')
Output: Markdown text explanation
```

```
Query: "What is the difference between Basic RAG and HyDE?"
Tool: query_architecture_patterns(query='Basic RAG vs HyDE')
Output: Text comparison (not structured matrix)
```

## API Usage

### Direct Usage (Python)

```python
from document_store.formatting import create_service

# Create service (uses env vars for Gemini/Ollama config)
service = create_service()

# Generate structured output
result = service.generate_structured_output(
    content="<document content>",
    query="Extract techniques catalog",
    schema_name="techniques_catalog",  # or "table", "list", "comparison"
    output_format="csv",  # or "json", "markdown", "html", "yaml"
    validate=True
)

if result["success"]:
    print(result["data"])  # Formatted output
    print(result["validation"])  # Validation results
else:
    print(result["error"])
```

### Via Agent Tools

The agent automatically uses these tools based on query analysis:

```python
# In agent_base.py tools
from document_store.formatting import create_service

def generate_structured_table(source_filter: str, output_format: str = "csv"):
    """Generate table with schema validation."""
    doc_result = get_complete_document(source_filter)
    service = create_service()

    return service.generate_structured_output(
        content=doc_result["content"],
        query=f"Extract as {output_format}",
        schema_name="table",
        output_format=output_format
    )
```

## Schemas

### Generic Schemas

#### TableSchema
```python
{
    "table_name": str,
    "description": Optional[str],
    "columns": List[str],
    "rows": List[Dict[str, Any]],
    "total_rows": int,
    "source_document": Optional[str]
}
```

#### ListSchema
```python
{
    "list_name": str,
    "description": Optional[str],
    "items": List[Dict[str, Any]],
    "total_items": int,
    "categories": Optional[List[str]]
}
```

#### ComparisonSchema
```python
{
    "comparison_name": str,
    "description": Optional[str],
    "entities": List[str],
    "dimensions": List[str],
    "matrix": List[Dict[str, Any]],
    "summary": Optional[str]
}
```

### Specialized Schemas

#### TechniquesCatalog
```python
{
    "catalog_name": str,
    "total_techniques": int,
    "techniques": List[TechniqueRow],
    "phases": List[str],
    "categories": List[str]
}

# TechniqueRow
{
    "phase": str,
    "category": str,
    "technique": str,
    "description": str,
    "process_framework": Optional[str],
    "usage": Optional[str],
    "lifecycle_steps": Optional[str]
}
```

## Supported Output Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| CSV | `.csv` | Spreadsheet import, data processing |
| TSV | `.tsv` | Tab-separated for specialized tools |
| JSON | `.json` | API responses, programmatic processing |
| Markdown | `.md` | Documentation, human-readable tables |
| HTML | `.html` | Web display, email reports |
| YAML | `.yaml` | Configuration files, nested data |

## Configuration

### Environment Variables

```bash
# Gemini Configuration (for structured output)
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.0-flash-exp  # Supports native structured output

# Ollama Configuration (alternative)
OLLAMA_MODEL=qwen3:14b
OLLAMA_BASE_URL=http://localhost:11434/v1

# Which to use for structured output
USE_OLLAMA_EVAL=false  # false=Gemini, true=Ollama
```

### Model Requirements

**Gemini (Recommended):**
- Models: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`
- Native structured output support via `response_schema`
- Faster and more reliable

**Ollama (Alternative):**
- Models: `qwen3:14b`, `gemma2:27b`, `llama3.1:70b`
- JSON mode via OpenAI-compatible API
- Requires local Ollama server

## Testing

### Run Tests

```bash
# Basic tests (no LLM required)
cd pattern-query-app
python3 scripts/test_structured_output.py

# With LLM integration (requires API key or Ollama)
export GEMINI_API_KEY=your-key
python3 scripts/test_structured_output.py
```

### Test Coverage

1. **Schema Registry Tests**
   - Schema listing and descriptions
   - Schema inference from queries
   - Schema retrieval

2. **Format Converter Tests**
   - JSON → CSV conversion
   - JSON → Markdown table
   - JSON → HTML table
   - Data integrity preservation

3. **Validator Tests**
   - CSV structure validation
   - JSON schema validation (Pydantic)
   - Content completeness checks

4. **LLM Integration Tests** (if configured)
   - Table extraction from markdown
   - Schema compliance
   - Format conversion accuracy

## Comparison: Before vs After

### Before (Prompt-Based CSV)

❌ **Issues:**
- 352-line prompt with CSV formatting rules
- Inconsistent output (markdown fences, quoting issues)
- Content truncation/summarization
- No validation
- Brittle and hard to maintain

```
User: "List techniques as CSV"
Agent: <reads 352-line CSV formatting rules>
Agent: <manually formats as CSV>
Output: ```csv
Phase,Category,Technique
... (sometimes with formatting errors)
```
```

### After (Structured Output)

✅ **Benefits:**
- LLM generates schema-compliant JSON
- Automatic validation via Pydantic
- Clean format conversion
- Consistent, reliable output
- Easy to maintain and extend

```
User: "List techniques as CSV"
Agent: <detects structured output request>
Agent: Uses generate_structured_table() tool
LLM: <extracts data with TechniquesCatalog schema>
Validator: <validates against schema>
Converter: <converts JSON to CSV>
Output: Clean, valid CSV (no markdown fences, proper quoting)
```

## Benefits

### Reliability
- ✅ Schema-based validation ensures correctness
- ✅ No manual parsing or string manipulation
- ✅ Consistent output across queries

### Flexibility
- ✅ Easy to add new output formats
- ✅ Support for multiple schemas
- ✅ Format-agnostic architecture (JSON as intermediate)

### Maintainability
- ✅ Less prompt engineering
- ✅ More code-based logic
- ✅ Clear separation of concerns

### Quality
- ✅ Better error handling
- ✅ Validation at multiple levels
- ✅ Content completeness verification

## Troubleshooting

### Issue: ImportError for create_service

**Solution:** Ensure you're using the updated `__init__.py`:
```python
from .structured_output import StructuredOutputService, create_service
```

### Issue: Pydantic ValidationError

**Solution:** Check that LLM output matches the expected schema:
```python
result = service.generate_structured_output(..., validate=True)
if not result["success"]:
    print(result["validation"]["errors"])
```

### Issue: CSV Formatting Issues

**Solution:** Use the structured output tools instead of prompt-based formatting:
```python
# Instead of manual formatting with get_complete_document()
# Use generate_structured_table()
result = generate_structured_table(
    source_filter='ai-development-techniques',
    output_format='csv'
)
```

### Issue: Agent Not Using Structured Output Tools

**Solution:** Check query phrasing - agent decides based on intent:
```
❌ "Show me techniques" → May use standard tools
✅ "List techniques as CSV" → Uses structured output tools
✅ "Create a table of techniques" → Uses structured output tools
```

## Future Enhancements

### Planned Features

1. **Additional Schemas**
   - Healthcare-specific schemas (patient records, clinical notes)
   - Metrics and evaluation schemas
   - Configuration schemas

2. **More Output Formats**
   - Excel (`.xlsx`) with formatting
   - PDF tables
   - LaTeX tables for academic papers

3. **Enhanced Validation**
   - Cross-referencing with source content
   - Semantic validation (not just schema)
   - Duplicate detection

4. **Performance Optimization**
   - Caching of structured outputs
   - Parallel extraction for large documents
   - Streaming for very large tables

## References

- Schema definitions: [`src/document_store/formatting/schemas.py`](../src/document_store/formatting/schemas.py)
- Service implementation: [`src/document_store/formatting/structured_output.py`](../src/document_store/formatting/structured_output.py)
- Agent tools: [`.adk/agents/_shared/agent_base.py`](../.adk/agents/_shared/agent_base.py)
- Tests: [`scripts/test_structured_output.py`](../scripts/test_structured_output.py)
