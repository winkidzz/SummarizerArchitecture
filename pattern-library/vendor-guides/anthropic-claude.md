# Anthropic Claude Vendor Implementation Guide

## Overview

This guide provides comprehensive implementation guidance for building healthcare AI summarization systems using Anthropic Claude models. Claude excels at medical reasoning, structured outputs, and long-context understanding, making it ideal for healthcare applications.

## Model Selection

### Claude 3.5 Sonnet (Recommended for Production)
- **Model ID**: `claude-3-5-sonnet-20241022`
- **Context Window**: 200,000 tokens
- **Best For**: Clinical note generation, patient summarization, complex medical reasoning
- **Strengths**: Excellent medical accuracy, low hallucination rates, strong reasoning
- **Cost**: Mid-tier ($$)
- **Speed**: Fast (2-3 seconds for typical requests)

### Claude 3.5 Haiku (Cost-Optimized)
- **Model ID**: `claude-3-5-haiku-20241022`
- **Context Window**: 200,000 tokens
- **Best For**: High-volume simple summaries, real-time applications, hypothesis generation (HyDE)
- **Strengths**: Very fast, cost-effective, good for straightforward tasks
- **Cost**: Low ($)
- **Speed**: Very fast (< 1 second)

### Claude 3 Opus (Maximum Capability)
- **Model ID**: `claude-3-opus-20240229`
- **Context Window**: 200,000 tokens
- **Best For**: Complex diagnostic reasoning, critical clinical decisions, research synthesis
- **Strengths**: Highest accuracy, best reasoning, lowest hallucination
- **Cost**: High ($$$)
- **Speed**: Slower (4-6 seconds)

**Healthcare Recommendation**: Use Claude 3.5 Sonnet for 90% of healthcare applications. Reserve Opus for critical clinical decision support.

## Healthcare Compliance

### HIPAA Business Associate Agreement (BAA)

**Availability**: ✅ Yes - Enterprise plan required

**Setup Process**:
1. Contact Anthropic sales for Enterprise plan
2. Execute BAA before processing any PHI
3. Enable audit logging
4. Configure data retention policies

**Key Provisions**:
- Data encryption at rest and in transit
- No model training on customer data
- Audit trail for all API calls
- Data deletion upon request
- Incident response procedures

### SOC 2 Type II Compliance
- ✅ Certified
- Regular third-party audits
- Security controls verified

### Data Residency
- US-based data centers
- Data does not leave specified regions
- Contact Anthropic for specific regional requirements

## Core Features for Healthcare

### 1. Long Context Window (200K tokens)

**Use Case**: Process extensive patient histories

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

# Process 10 years of patient records in single request
patient_history = load_patient_records(patient_id="12345", years=10)
# Assume this is ~150,000 tokens

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": f"""Analyze this patient's 10-year medical history and create a comprehensive summary.

PATIENT HISTORY (150K tokens):
{patient_history}

Provide:
1. Chronic condition progression
2. Medication history and changes
3. Significant procedures and outcomes
4. Current clinical status
5. Risk factors and recommendations"""
    }]
)

summary = message.content[0].text
```

**Benefits**:
- No need to chunk long documents
- Better context understanding
- Reduced hallucination (full context available)

### 2. Structured Outputs (Tool Use)

**Use Case**: Generate structured SOAP notes

```python
# Define SOAP note schema
soap_schema = {
    "name": "generate_soap_note",
    "description": "Generate a structured SOAP note from clinical encounter",
    "input_schema": {
        "type": "object",
        "properties": {
            "subjective": {
                "type": "object",
                "properties": {
                    "chief_complaint": {"type": "string"},
                    "hpi": {"type": "string"},
                    "ros": {"type": "object"}
                },
                "required": ["chief_complaint", "hpi"]
            },
            "objective": {
                "type": "object",
                "properties": {
                    "vitals": {"type": "object"},
                    "physical_exam": {"type": "string"}
                }
            },
            "assessment": {
                "type": "object",
                "properties": {
                    "diagnoses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "icd10": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["diagnoses"]
            },
            "plan": {
                "type": "object",
                "properties": {
                    "medications": {"type": "array"},
                    "orders": {"type": "array"},
                    "follow_up": {"type": "string"}
                }
            }
        },
        "required": ["subjective", "objective", "assessment", "plan"]
    }
}

# Generate structured SOAP note
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    tools=[soap_schema],
    messages=[{
        "role": "user",
        "content": f"""Generate a SOAP note from this encounter:

ENCOUNTER DATA:
{encounter_transcript}

Use the generate_soap_note tool to structure your response."""
    }]
)

# Extract structured note
tool_use = next((block for block in message.content if block.type == "tool_use"), None)
if tool_use:
    soap_note = tool_use.input
    print(json.dumps(soap_note, indent=2))
```

**Benefits**:
- Guaranteed JSON structure
- Type validation
- Easier EHR integration
- Reduced parsing errors

### 3. Prompt Caching (Cost Optimization)

**Use Case**: Reuse system prompts across multiple patients

```python
# Cache system prompt for multiple uses
system_prompt = """You are a clinical AI assistant specializing in cardiology.
When summarizing patient records:
1. Prioritize cardiac-related information
2. Use standard medical terminology
3. Note any contraindications
4. Highlight trends over time
5. Flag critical findings

[... extensive 10,000 token clinical guidelines ...]
"""

# First request - creates cache
message1 = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    system=[{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"}  # Cache this
    }],
    messages=[{
        "role": "user",
        "content": f"Summarize patient record for {patient_1}"
    }]
)

# Second request - uses cached system prompt (90% cost reduction on cached tokens)
message2 = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    system=[{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"}  # Reuses cache
    }],
    messages=[{
        "role": "user",
        "content": f"Summarize patient record for {patient_2}"
    }]
)

# Check cache performance
print(f"Cache read tokens: {message2.usage.cache_read_input_tokens}")
print(f"Cache creation tokens: {message2.usage.cache_creation_input_tokens}")
```

**Cost Savings**:
- Cached tokens: 90% discount
- Ideal for: System prompts, clinical guidelines, repeated context
- Cache lifetime: 5 minutes (ephemeral)

**Security Note**: ⚠️ NEVER cache PHI! Only cache non-patient-specific content.

### 4. Vision Capabilities (Multi-Modal)

**Use Case**: Analyze medical imaging reports with embedded images

```python
import base64

# Read medical image
with open("chest_xray.jpg", "rb") as image_file:
    image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            },
            {
                "type": "text",
                "text": """Analyze this chest X-ray and provide:
1. Key findings
2. Comparison with previous X-ray (if available in history)
3. Clinical significance
4. Recommendations

Note: You are assisting a radiologist, not providing final diagnosis."""
            }
        ]
    }]
)

findings = message.content[0].text
```

**Healthcare Applications**:
- Radiology report generation assistance
- Pathology slide analysis
- Dermatology image assessment
- Wound care documentation

**Important**: Vision should assist clinicians, not replace diagnostic judgment.

## RAG Pattern Implementations

### Basic RAG with Claude

```python
from document_store.storage.vector_store import VectorStore

vector_store = VectorStore()

def claude_basic_rag(query: str, patient_id: str = None) -> str:
    """Basic RAG pattern with Claude."""

    # Retrieve relevant documents
    filter_criteria = {"patient_id": patient_id} if patient_id else {}
    results = vector_store.query(
        query=query,
        filter=filter_criteria,
        n_results=5
    )

    context = "\n\n".join(results['documents'])

    # Generate with Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Answer the question using the provided medical records.

MEDICAL RECORDS:
{context}

QUESTION: {query}

Provide a comprehensive, clinically accurate answer:"""
        }]
    )

    return message.content[0].text
```

### HyDE RAG with Claude

```python
def claude_hyde_rag(query: str) -> str:
    """HyDE pattern optimized for Claude."""

    # Step 1: Generate hypothetical medical answer
    hypothesis_message = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Use Haiku for cost savings
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"""Generate a detailed hypothetical medical answer to: {query}

Write as if you have the information. Use medical terminology."""
        }]
    )

    hypothesis = hypothesis_message.content[0].text

    # Step 2: Retrieve using hypothesis
    results = vector_store.query(query=hypothesis, n_results=5)
    context = "\n\n".join(results['documents'])

    # Step 3: Final answer with Sonnet
    final_message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""CONTEXT:\n{context}\n\nQUESTION: {query}\n\nAnswer:"""
        }]
    )

    return final_message.content[0].text
```

### Self-RAG with Claude

```python
def claude_self_rag(query: str) -> dict:
    """Self-RAG pattern with retrieval and validation."""

    # Retrieve documents
    results = vector_store.query(query=query, n_results=5)
    context = "\n\n".join(results['documents'])

    # Generate answer
    answer_message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        }]
    )

    answer = answer_message.content[0].text

    # Self-validate
    validation_message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Evaluate this answer for clinical accuracy and completeness.

CONTEXT: {context}
QUESTION: {query}
ANSWER: {answer}

Provide:
1. Accuracy score (0-100)
2. Completeness score (0-100)
3. Specific issues or concerns
4. Recommendation: ACCEPT or REGENERATE"""
        }]
    )

    validation = validation_message.content[0].text

    return {
        "answer": answer,
        "validation": validation,
        "context": context
    }
```

## Best Practices

### 1. System Prompts for Healthcare

```python
CLINICAL_SYSTEM_PROMPT = """You are a clinical AI assistant. Follow these rules:

ACCURACY:
- Base answers ONLY on provided clinical data
- Never speculate beyond available information
- Clearly state when information is insufficient
- Use evidence-based medical knowledge

SAFETY:
- Highlight critical findings (sepsis, MI, stroke symptoms)
- Note drug interactions and contraindications
- Flag abnormal vital signs or labs
- This is DECISION SUPPORT, not replacement for clinical judgment

COMPLIANCE:
- Maintain patient privacy (never reveal PHI inappropriately)
- Use standardized medical terminology
- Include relevant ICD-10 codes when applicable
- Document limitations and uncertainties

COMMUNICATION:
- Clear, concise clinical language
- Bullet points for key information
- Highlight urgency levels
- Cite specific data points from records"""

# Use in every request
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    system=CLINICAL_SYSTEM_PROMPT,
    messages=[...]
)
```

### 2. Temperature Settings

```python
# For clinical documentation (high accuracy needed)
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    temperature=0.1,  # Low temperature for consistency
    messages=[...]
)

# For creative clinical education content
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    temperature=0.7,  # Higher temperature for variety
    messages=[...]
)
```

**Healthcare Recommendation**: Use temperature 0.0-0.3 for clinical documentation and decision support.

### 3. Error Handling

```python
from anthropic import APIError, RateLimitError
import time

def robust_claude_call(messages, max_retries=3):
    """Robust API call with retry logic."""

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=messages
            )
            return message.content[0].text

        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise

        except APIError as e:
            print(f"API Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

    return None
```

### 4. Audit Logging

```python
import logging
from datetime import datetime

audit_logger = logging.getLogger("claude_audit")

def audited_claude_call(query, patient_id, user_id):
    """Claude API call with audit logging."""

    # Log request
    audit_logger.info({
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "patient_id": patient_id,
        "query_length": len(query),
        "model": "claude-3-5-sonnet-20241022"
    })

    # Make API call
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{"role": "user", "content": query}]
    )

    answer = message.content[0].text

    # Log response
    audit_logger.info({
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "patient_id": patient_id,
        "response_length": len(answer),
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens
    })

    return answer
```

## Cost Optimization

### Token Usage Optimization

```python
# Estimate costs before making requests
def estimate_cost(input_text: str, output_tokens: int = 1000, model: str = "claude-3-5-sonnet-20241022"):
    """Estimate Claude API cost."""

    # Approximate tokenization (1 token ≈ 4 characters)
    input_tokens = len(input_text) // 4

    # Pricing (as of Jan 2025 - verify current pricing)
    pricing = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.00 / 1_000_000,    # $3 per million input tokens
            "output": 15.00 / 1_000_000   # $15 per million output tokens
        },
        "claude-3-5-haiku-20241022": {
            "input": 0.25 / 1_000_000,
            "output": 1.25 / 1_000_000
        }
    }

    model_pricing = pricing[model]
    cost = (input_tokens * model_pricing["input"] +
            output_tokens * model_pricing["output"])

    return {
        "estimated_cost": cost,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens
    }

# Example
cost_est = estimate_cost(patient_history, output_tokens=2000)
print(f"Estimated cost: ${cost_est['estimated_cost']:.4f}")
```

### Model Selection Strategy

```python
def select_optimal_model(task_complexity: str, budget: str) -> str:
    """Choose optimal Claude model based on task and budget."""

    if budget == "low" or task_complexity == "simple":
        return "claude-3-5-haiku-20241022"
    elif task_complexity == "critical":
        return "claude-3-opus-20240229"
    else:
        return "claude-3-5-sonnet-20241022"

# Example usage
model = select_optimal_model(task_complexity="moderate", budget="standard")
```

## Monitoring and Observability

### Track API Usage

```python
import anthropic

# Enable detailed usage tracking
client = anthropic.Anthropic(
    api_key="your-api-key",
    # Add custom headers for tracking
    default_headers={"X-Application": "HealthcareSummarizer"}
)

def track_usage(message_response):
    """Track Claude API usage metrics."""

    usage = message_response.usage
    metrics = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_creation_tokens": getattr(usage, 'cache_creation_input_tokens', 0),
        "cache_read_tokens": getattr(usage, 'cache_read_input_tokens', 0)
    }

    # Send to monitoring system (e.g., CloudWatch, Datadog)
    send_to_monitoring(metrics)

    return metrics
```

## Security Considerations

### Input Sanitization

```python
import re

def sanitize_medical_query(query: str) -> str:
    """Sanitize query before sending to Claude."""

    # Remove potential injection attempts
    query = re.sub(r'<script.*?</script>', '', query, flags=re.DOTALL | re.IGNORECASE)

    # Limit length
    if len(query) > 10000:
        raise ValueError("Query too long")

    # Log sanitization
    audit_logger.info(f"Query sanitized, length: {len(query)}")

    return query
```

### PHI Handling

```python
# NEVER cache PHI
def create_safe_prompt(system_prompt: str, patient_query: str):
    """Create prompt with safe caching."""

    return {
        "system": [{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"}  # Safe: no PHI in system prompt
        }],
        "messages": [{
            "role": "user",
            "content": patient_query  # NOT cached - contains PHI
        }]
    }
```

## References

- [Claude API Documentation](https://docs.anthropic.com/claude/reference)
- [Claude for Enterprise Healthcare](https://www.anthropic.com/enterprise)
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Tool Use (Structured Outputs)](https://docs.anthropic.com/claude/docs/tool-use)
- [Prompt Caching](https://docs.anthropic.com/claude/docs/prompt-caching)

## Version History

- **v1.0** (2025-11-09): Initial Anthropic Claude vendor guide
