# Troubleshooting Guide

Common issues and solutions for the AI Summarization Reference Architecture project.

## Document Store Issues

### ChromaDB Embedding Errors

**Error**: `'function' object has no attribute 'name'`

**Solution**: Use `SentenceTransformerEmbeddingFunction` wrapper:
```python
from chromadb.utils import embedding_functions

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
```

**Error**: `Expected metadata to be a non-empty dict`

**Solution**: Ensure metadata is always a dictionary with at least one key:
```python
metadata = metadata.copy() if metadata else {}
metadata.setdefault("source", str(source_path))
metadata.setdefault("file_path", str(source_path))
```

### Document Processing Errors

**Error**: `docling is not installed`

**Solution**: Install docling:
```bash
pip install docling
```

**Error**: Document format not supported

**Solution**: Check supported formats (PDF, DOCX, PPTX, TXT, MD). Convert unsupported formats first.

## Agent Integration Issues

### Ollama Connection Errors

**Error**: `Connection refused` or `Ollama server not available`

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify model is available: `ollama list`

**Error**: Model not found

**Solution**: Pull the model first:
```bash
ollama pull llama3
```

### Google ADK Not Available

**Error**: `Google ADK not installed` (warning, not error)

**Solution**: This is expected if Google ADK is not installed. The system will fall back to direct RAG queries. To use ADK:
1. Install Google ADK when available
2. Configure ADK credentials
3. Update orchestrator to use ADK agent

## Vector Store Issues

### Collection Not Found

**Error**: `Collection does not exist`

**Solution**: Collections are created automatically. If missing:
```python
collection = client.get_or_create_collection(
    name="patterns",
    embedding_function=embedding_fn
)
```

### Embedding Dimension Mismatch

**Error**: Embedding dimensions don't match

**Solution**: Use consistent embedding model. Reset vector store if needed:
```python
vector_store.reset()
```

## Performance Issues

### Slow Query Performance

**Symptoms**: Queries taking >5 seconds

**Solutions**:
1. Reduce `n_results` parameter
2. Use faster embedding model (e.g., `all-MiniLM-L6-v2`)
3. Enable caching for repeated queries
4. Optimize vector store (indexing, clustering)

### High Memory Usage

**Symptoms**: Out of memory errors

**Solutions**:
1. Process documents in batches
2. Use smaller embedding models
3. Limit vector store size
4. Clear cache periodically

## Healthcare Data Integration Issues

### FHIR API Connection Errors

**Error**: Authentication failed

**Solution**:
1. Verify OAuth 2.0 credentials
2. Check token expiration
3. Verify API endpoint URL
4. Check network connectivity

### BigQuery Access Errors

**Error**: Permission denied

**Solution**:
1. Verify service account has BigQuery access
2. Check IAM permissions
3. Verify project ID is correct
4. Check dataset permissions

### Pub/Sub Subscription Errors

**Error**: Subscription not found

**Solution**:
1. Verify subscription exists
2. Check project ID
3. Verify service account permissions
4. Check subscription name spelling

## Testing Issues

### Test Script Failures

**Error**: Component initialization failed

**Solution**:
1. Check all dependencies installed: `pip install -r requirements.txt`
2. Verify Python version (3.8+)
3. Check environment variables
4. Review error messages in test results JSON

### Example Script Errors

**Error**: Import errors

**Solution**:
1. Ensure you're in project root directory
2. Check Python path includes `src/`
3. Verify package structure
4. Install package: `pip install -e .`

## Common Solutions

### Reset Everything

If all else fails, reset the document store:

```python
from document_store.storage.vector_store import VectorStore

vector_store = VectorStore(collection_name="patterns")
vector_store.reset()  # Clears all data
```

### Reinstall Dependencies

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Check Logs

Review logs for detailed error information:
- Component logs: Check console output
- Test results: `data/test_results.json`
- Application logs: Check logging configuration

## RAG Pattern Issues

### HyDE Pattern Problems

**Issue**: Hypothesis generation produces poor quality or irrelevant content

**Solutions**:
1. Improve hypothesis generation prompt with domain context
2. Use better model for hypothesis (Sonnet instead of Haiku)
3. Add validation layer before retrieval
4. Try multi-hypothesis approach for diversity
5. Fall back to basic RAG if hypothesis quality is low

**Issue**: HyDE is too slow (>10 seconds)

**Solutions**:
1. Use faster model for hypothesis (Haiku)
2. Cache hypotheses for common queries
3. Reduce max_tokens for hypothesis generation
4. Implement async/parallel processing
5. Consider adaptive routing (HyDE only for complex queries)

### RAPTOR Pattern Problems

**Issue**: Tree building takes too long (hours)

**Solutions**:
1. Reduce `max_layers` parameter (try 2-3 instead of 4-5)
2. Increase `cluster_size` (fewer clusters = faster)
3. Use faster model for summarization (Haiku)
4. Process clusters in parallel
5. Build tree offline during off-hours

**Issue**: Query returns irrelevant results from wrong tree layer

**Solutions**:
1. Adjust `nodes_per_layer` parameter
2. Tune clustering algorithm parameters
3. Improve layer-specific retrieval weights
4. Add metadata filtering by layer relevance
5. Re-evaluate tree structure and rebuild if needed

### Streaming RAG Issues

**Issue**: Data not processing in real-time

**Solutions**:
1. Check message queue connection (Kafka/RabbitMQ)
2. Verify buffer size settings
3. Check for processing bottlenecks
4. Monitor stream lag metrics
5. Scale consumers if needed

**Issue**: Missing events or data loss

**Solutions**:
1. Verify at-least-once delivery guarantees
2. Check consumer acknowledgment settings
3. Monitor dead letter queue
4. Implement idempotency for duplicate handling
5. Add event replay capability

## LLM API Issues

### Anthropic Claude Issues

**Error**: `rate_limit_error` - Too many requests

**Solutions**:
1. Implement exponential backoff retry logic
2. Add rate limiting to your application
3. Use batch processing where possible
4. Upgrade to higher rate limit tier
5. Cache responses for repeated queries

**Error**: `overloaded_error` - Service temporarily unavailable

**Solutions**:
1. Retry with exponential backoff
2. Implement circuit breaker pattern
3. Have fallback to alternative model/vendor
4. Queue requests for later processing
5. Monitor Anthropic status page

**Error**: Token limit exceeded (> 200K)

**Solutions**:
1. Chunk documents before sending
2. Use summarization for very long context
3. Implement sliding window approach
4. Filter less relevant content
5. Consider RAPTOR for hierarchical processing

### Azure OpenAI Issues

**Error**: Authentication failed (401)

**Solutions**:
1. Verify API key is correct and active
2. Check Azure AD authentication settings
3. Regenerate API key if expired
4. Verify endpoint URL format
5. Check subscription status

**Error**: Deployment not found (404)

**Solutions**:
1. Verify deployment name spelling
2. Check deployment exists in Azure portal
3. Verify correct region/endpoint
4. Ensure deployment is not paused
5. Check subscription has access

**Error**: Content filtering triggered

**Solutions**:
1. Review content policy guidelines
2. Sanitize input before sending
3. Adjust content filter settings (if permitted)
4. Add pre-filtering layer
5. Request content filter exemption for healthcare use

### Google Vertex AI Issues

**Error**: Permission denied

**Solutions**:
1. Verify service account has Vertex AI permissions
2. Check IAM roles (Vertex AI User)
3. Enable Vertex AI API if not enabled
4. Verify project ID is correct
5. Check quota limits

**Error**: Model not available in region

**Solutions**:
1. Check model availability by region
2. Switch to supported region
3. Use alternative model
4. Request model access for region
5. Check quota and limits

## Healthcare-Specific Issues

### FHIR Integration Problems

**Error**: Resource not found

**Solutions**:
1. Verify resource ID format (e.g., `Patient/12345`)
2. Check resource exists in FHIR server
3. Verify search parameters syntax
4. Check FHIR version compatibility (R4 vs. STU3)
5. Review FHIR server logs

**Error**: Invalid FHIR resource format

**Solutions**:
1. Validate JSON against FHIR schema
2. Check required fields are present
3. Verify coding systems (LOINC, SNOMED)
4. Use FHIR validator tool
5. Review FHIR specification for resource type

**Error**: Unauthorized access to patient data

**Solutions**:
1. Verify OAuth 2.0 token is valid
2. Check SMART on FHIR scopes
3. Verify patient consent is documented
4. Check EHR access policies
5. Review BAA and HIPAA compliance

### HL7 Message Processing Issues

**Error**: Message parsing failed

**Solutions**:
1. Verify HL7 v2.x version compatibility
2. Check segment delimiters
3. Validate message structure
4. Use HL7 parser library (python-hl7)
5. Log raw message for debugging

**Error**: Patient matching failed

**Solutions**:
1. Verify MRN/patient identifiers
2. Check identifier system/namespace
3. Implement fuzzy matching if needed
4. Validate patient demographics
5. Review matching algorithm

### Clinical Data Quality Issues

**Issue**: Inaccurate medical terminology extraction

**Solutions**:
1. Use medical NLP libraries (scispaCy, MedCAT)
2. Implement clinical vocabulary normalization
3. Add medical terminology validation
4. Use medical-specific embedding models
5. Provide more clinical context in prompts

**Issue**: Missing critical clinical information

**Solutions**:
1. Verify data completeness in source
2. Improve information extraction prompts
3. Add validation for required fields
4. Implement data quality checks
5. Alert on missing critical data

**Issue**: Hallucinated medical information

**Solutions**:
1. Use Self-RAG for validation
2. Lower temperature setting (0.0-0.1)
3. Require citations from source data
4. Implement fact-checking layer
5. Add human review for critical content

## Security & Compliance Issues

### PHI Exposure in Logs

**Issue**: Patient information logged in plaintext

**Solutions**:
1. Implement log sanitization
2. Use structured logging with PHI filters
3. Encrypt logs at rest and in transit
4. Set appropriate log retention policies
5. Audit log access regularly

### BAA Compliance Issues

**Error**: Vendor doesn't have BAA

**Solutions**:
1. Only use vendors with signed BAA
2. For development: use synthetic data only
3. Switch to BAA-compliant vendor
4. Process data on-premises if needed
5. Document compliance requirements

### Prompt Injection Detected

**Issue**: Suspicious patterns in user queries

**Solutions**:
1. Implement input sanitization
2. Use security boundaries in system prompts
3. Monitor for jailbreak attempts
4. Block known malicious patterns
5. Alert security team for investigation

## Performance Optimization

### Slow Response Times

**Issue**: Queries taking >10 seconds

**Diagnosis**:
1. Check where time is spent (profiling)
2. Monitor API latency metrics
3. Measure retrieval time separately
4. Track LLM inference time
5. Identify bottlenecks

**Solutions**:
1. **Retrieval Optimization**:
   - Reduce `n_results` parameter
   - Use faster embedding model
   - Implement caching
   - Optimize vector store indexing

2. **LLM Optimization**:
   - Use faster model (Haiku vs. Sonnet)
   - Reduce max_tokens
   - Enable streaming responses
   - Implement prompt caching

3. **Architecture Optimization**:
   - Parallel processing where possible
   - Async/await for I/O operations
   - Connection pooling
   - Load balancing

### High Cost Issues

**Issue**: API costs exceeding budget

**Solutions**:
1. **Model Selection**:
   - Use Haiku for simple tasks
   - Reserve Opus/Sonnet for complex queries
   - Implement adaptive model routing

2. **Caching**:
   - Cache common query results
   - Use prompt caching (save 90% on cached tokens)
   - Cache embeddings

3. **Token Optimization**:
   - Reduce retrieved context length
   - Compress prompts
   - Use smaller max_tokens
   - Implement smart chunking

4. **Monitoring**:
   - Track cost per query
   - Set budget alerts
   - Monitor token usage
   - Identify expensive queries

### Memory Issues

**Issue**: Out of memory errors

**Solutions**:
1. Process documents in batches (batch_size=10)
2. Use generators instead of loading all data
3. Clear caches periodically
4. Implement streaming for large results
5. Increase system memory or use distributed processing

## Debugging Tips

### Enable Verbose Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# For specific libraries
logging.getLogger('anthropic').setLevel(logging.DEBUG)
logging.getLogger('chromadb').setLevel(logging.DEBUG)
```

### Test Individual Components

```python
# Test embedding generation
from document_store.storage.vector_store import VectorStore

vector_store = VectorStore()
embedding = vector_store.embed_query("test query")
print(f"Embedding dimension: {len(embedding)}")

# Test LLM API
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "test"}]
)
print(response.content[0].text)

# Test FHIR connection
from document_store.healthcare.fhir_client import FHIRClient
fhir_client = FHIRClient(base_url="https://fhir.example.org")
patient = fhir_client.get_patient("12345")
print(f"Patient: {patient['name']}")
```

### Monitor API Usage

```python
# Track token usage
def track_api_call(response):
    usage = response.usage
    print(f"Input tokens: {usage.input_tokens}")
    print(f"Output tokens: {usage.output_tokens}")
    if hasattr(usage, 'cache_read_input_tokens'):
        print(f"Cache read: {usage.cache_read_input_tokens}")
        print(f"Cache write: {usage.cache_creation_input_tokens}")
```

### Validate Data Quality

```python
# Check FHIR resource structure
import jsonschema

def validate_fhir_resource(resource, resource_type):
    # Load FHIR schema
    schema = load_fhir_schema(resource_type)

    try:
        jsonschema.validate(resource, schema)
        print("✓ Valid FHIR resource")
    except jsonschema.ValidationError as e:
        print(f"✗ Invalid: {e.message}")
```

## Known Issues

### Current Limitations

1. **RAPTOR tree building is slow** - Can take hours for large document sets. Use offline processing.

2. **HyDE may increase hallucination risk** - Hypothesis might be incorrect. Use Self-RAG validation for critical applications.

3. **Real-time streaming has ~3-5 second latency** - Due to LLM inference time. Consider pre-computation for time-critical alerts.

4. **Prompt caching requires identical prompts** - Small changes break cache. Careful prompt engineering needed.

5. **Vision capabilities are preview** - Not all medical image types supported. Verify with your specific image formats.

## Getting Help

1. **Check Documentation**: Review relevant pattern documentation
2. **Review Test Results**: Check `data/test_results.json` for specific errors
3. **Check Logs**: Review console output and log files
4. **Verify Setup**: Run `python scripts/initialize_and_test.py` to verify setup
5. **Security Issues**: Contact your security team immediately
6. **Vendor-Specific**: Consult vendor documentation and support

## Emergency Procedures

### Production System Down

1. **Immediate Actions**:
   - Alert on-call team
   - Check system health dashboard
   - Review recent changes/deployments
   - Check vendor status pages

2. **Fallback Procedures**:
   - Switch to backup region/deployment
   - Activate disaster recovery plan
   - Fall back to manual processes if needed
   - Communicate with clinical staff

3. **Post-Incident**:
   - Document incident timeline
   - Perform root cause analysis
   - Update runbooks
   - Implement preventive measures

### Security Incident

1. **Suspected PHI Breach**:
   - Immediately isolate affected systems
   - Alert security team and compliance officer
   - Preserve logs and evidence
   - Follow breach notification procedures
   - Contact BAA vendors if applicable

2. **Malicious Activity Detected**:
   - Block suspicious IP/user
   - Review audit logs
   - Assess scope of compromise
   - Implement additional monitoring
   - Update security controls

## Version History

- **v1.0** (2025-11-08): Initial troubleshooting guide
- **v1.1** (2025-11-09): Added RAG pattern issues, LLM API troubleshooting, healthcare-specific issues, security & compliance, performance optimization, emergency procedures

