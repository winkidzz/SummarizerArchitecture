# Testing Guide

This guide explains the testing approach for the AI Summarization Reference Architecture project.

## Testing Philosophy

Following the project's "Extend, Don't Duplicate" principle:

- **No Separate Test Files**: Do not create isolated test files for every feature
- **Extend Existing Scripts**: Use and extend existing example scripts as test harnesses
- **Unified Testing**: Integrate tests into existing workflows
- **Script Evolution**: Evolve scripts to handle multiple scenarios

## Comprehensive Test Script

The main testing script is `scripts/initialize_and_test.py`, which:

1. **Extends Existing Components**: Uses the same components as example scripts
2. **Tests All Components**: Initializes and tests all major components
3. **Provides Unified Results**: Generates a comprehensive test summary
4. **Saves Results**: Outputs test results to JSON for analysis

### Running Tests

```bash
# Windows
py scripts/initialize_and_test.py

# Linux/Mac
python3 scripts/initialize_and_test.py
```

### Test Coverage

The script tests:

1. **Component Initialization**
   - Docling Processor
   - Vector Store (ChromaDB)
   - RAG Query Interface
   - Web Search Tool
   - ADK Agent (if available)
   - Ollama Agent (if available)
   - Orchestrator

2. **Document Processing**
   - Document conversion
   - Metadata handling
   - Format support

3. **Vector Store Operations**
   - Document addition
   - Query operations
   - Collection management

4. **RAG Query Interface**
   - Pattern querying
   - Result formatting
   - Filtering capabilities

5. **Web Search**
   - Search functionality
   - Result retrieval

6. **Orchestrator Integration**
   - End-to-end workflows
   - Document ingestion
   - Query operations

7. **Agent Integrations**
   - ADK Agent (if available)
   - Ollama Agent (if available)

## Extending Tests

To add new test cases, **extend** the existing test script rather than creating new files:

```python
# In scripts/initialize_and_test.py

def test_new_feature(self) -> Dict[str, Any]:
    """Test new feature - extends existing test pattern."""
    logger.info("\n" + "="*60)
    logger.info("TEST X: New Feature")
    logger.info("="*60)
    
    # Use existing components
    orchestrator = DocumentStoreOrchestrator(...)
    
    # Test new feature
    results = {}
    try:
        # Test implementation
        result = orchestrator.new_feature()
        results["new_feature"] = {"status": "success", "result": result}
        logger.info("✓ New feature test successful")
    except Exception as e:
        results["new_feature"] = {"status": "error", "error": str(e)}
        logger.error(f"✗ New feature test failed: {e}")
    
    # Add to results
    self.results["component_tests"]["new_feature"] = results
    return results
```

Then add to `run_all_tests()`:

```python
def run_all_tests(self) -> Dict[str, Any]:
    # ... existing tests ...
    self.test_new_feature()  # Add new test
    # ...
```

## Using Example Scripts as Tests

Example scripts in `examples/` can also serve as test harnesses:

### Example: Extending query_patterns.py

```python
# In examples/query_patterns.py

def test_additional_queries():
    """Extend existing query examples with test cases."""
    orchestrator = DocumentStoreOrchestrator(...)
    
    # Original examples
    queries = ["What is basic RAG?", ...]
    
    # Add test cases
    test_queries = [
        "Test query 1",
        "Test query 2",
    ]
    
    all_queries = queries + test_queries
    
    for query in all_queries:
        results = orchestrator.query_patterns(query)
        assert results['count'] >= 0  # Test assertion
        # ... more assertions
```

## Test Results

Test results are saved to `data/test_results.json` with:

- Component initialization status
- Individual test results
- Error messages
- Summary statistics

### Interpreting Results

- **Success**: Component/test works correctly
- **Error**: Component/test failed (needs fixing)
- **Warning**: Component available but not fully functional (e.g., Ollama not running)
- **Not Installed**: Optional component not installed (e.g., ADK, Ollama)

## Best Practices

1. **Extend, Don't Duplicate**: Always extend existing scripts
2. **Use Existing Components**: Reuse orchestrator and components
3. **Incremental Testing**: Add test cases to existing test methods
4. **Unified Results**: Use the same result format
5. **Documentation**: Document new test cases in this guide

## Continuous Testing

The test script can be run:

- **Before Commits**: Ensure all components work
- **After Changes**: Verify modifications don't break functionality
- **CI/CD**: Integrate into automated pipelines

## Troubleshooting

### Common Issues

1. **ChromaDB Embedding Errors**: Fixed by using `SentenceTransformerEmbeddingFunction`
2. **Ollama Connection**: Ensure Ollama service is running
3. **ADK Not Available**: Expected if Google ADK not installed
4. **Metadata Errors**: Ensure metadata is non-empty dict

### Fixing Issues

When fixing test failures:

1. Identify the failing component
2. Check error messages in test results
3. Fix the issue in the component code
4. Re-run tests to verify fix
5. Update test script if needed (extend, don't duplicate)

## Next Steps

- Add more test cases to existing test methods
- Extend example scripts with test assertions
- Integrate into CI/CD pipeline
- Add performance benchmarks

