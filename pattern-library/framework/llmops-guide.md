# LLMOps Guide

Operational practices for running LLM-powered applications in production — prompt management, cost control, observability, and reliability.

> **Scope**: This guide covers LLM-specific operational concerns. For general ML operations, see [MLOps Patterns](../patterns/ai-design/mlops/). For the underlying architecture framework, see [Architecture Framework](./architecture-framework.md).

---

## What Is LLMOps?

LLMOps extends traditional MLOps with practices specific to large language model applications:

| MLOps Concern | LLMOps Equivalent |
|---------------|-------------------|
| Model training pipeline | Prompt engineering + fine-tuning pipeline |
| Model registry | Prompt registry + model version management |
| Feature store | Context/retrieval pipeline (RAG) |
| Model monitoring | LLM observability (traces, token usage, quality) |
| A/B testing | Prompt A/B testing + model routing |
| CI/CD for models | CI/CD for prompts + RAG pipelines |
| Cost management | Token budget management + model routing |

---

## 1. Prompt Management

### Prompt Versioning

Treat prompts as code. Version, review, test, and deploy them with the same rigor as application code.

```
prompts/
├── clinical-summarization/
│   ├── v1.0.yaml          # Initial prompt
│   ├── v1.1.yaml          # Added ICD-10 extraction
│   ├── v2.0.yaml          # Restructured for Claude 3.5
│   └── evaluation/
│       ├── test-cases.jsonl
│       └── results-v2.0.json
├── medication-extraction/
│   ├── v1.0.yaml
│   └── ...
└── prompt-config.yaml      # Active version mappings
```

### Prompt Configuration Format

```yaml
# prompts/clinical-summarization/v2.0.yaml
name: clinical-summarization
version: "2.0"
description: "SOAP note summarization from clinical encounters"
model_compatibility:
  - claude-sonnet-4-5-20250929
  - gemini-2.0-flash
  - gpt-4o
system_prompt: |
  You are a clinical documentation assistant...
user_template: |
  Summarize the following encounter in SOAP format:
  {encounter_text}
parameters:
  temperature: 0.2
  max_tokens: 2000
metadata:
  author: "clinical-ai-team"
  created: "2026-02-05"
  evaluation_score: 0.92
  healthcare_reviewed: true
```

### Prompt Testing Pipeline

```
git push (prompt change)
  → CI runs prompt evaluation suite
  → Compare against baseline metrics
  → Auto-deploy if metrics improve
  → Flag for human review if metrics degrade
```

Key metrics to evaluate on each prompt change:
- **Accuracy**: Does the output match expected results?
- **Consistency**: Same input produces similar outputs across runs?
- **Safety**: Does it handle adversarial inputs correctly?
- **Cost**: Token usage within budget?
- **Latency**: Response time acceptable?

---

## 2. LLM Observability

### What to Trace

Every LLM call in production should capture:

| Dimension | What to Track | Why |
|-----------|---------------|-----|
| **Request** | Prompt text, model, parameters | Debugging, audit |
| **Response** | Output text, finish reason | Quality analysis |
| **Tokens** | Input tokens, output tokens, total | Cost tracking |
| **Latency** | Time to first token, total latency | Performance |
| **Quality** | Relevance score, faithfulness score | Drift detection |
| **Cost** | Cost per request | Budget management |
| **Errors** | Rate limits, timeouts, failures | Reliability |
| **RAG context** | Retrieved chunks, retrieval scores | Retrieval quality |

### Observability Stack

| Tool | Type | Strengths |
|------|------|-----------|
| **LangSmith** | Tracing + evaluation | Deep LangChain integration, prompt playground |
| **Langfuse** | Open-source tracing | Self-hostable, cost tracking, prompt management |
| **Arize Phoenix** | Open-source observability | LLM evaluation, embedding analysis |
| **Datadog LLM Observability** | APM integration | Enterprise monitoring, alerting |
| **Google Cloud Trace** | GCP native | Vertex AI integration |
| **OpenTelemetry + custom** | DIY | Full control, vendor-agnostic |

### Healthcare Observability Requirements

- **Audit trail**: Every LLM interaction must be logged for compliance
- **PHI detection**: Monitor for PHI leakage in outputs
- **Clinical accuracy tracking**: Flag outputs that contradict known guidelines
- **Response time SLAs**: Clinical workflows have strict latency requirements

---

## 3. Cost Management

### Token Economics

| Model | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Notes |
|-------|---------------------------|----------------------------|-------|
| Claude Opus 4.5 | $15.00 | $75.00 | Highest quality |
| Claude Sonnet 4.5 | $3.00 | $15.00 | Best quality/cost ratio |
| Claude Haiku 4.5 | $0.80 | $4.00 | Fastest, cheapest |
| GPT-4o | $2.50 | $10.00 | Strong general purpose |
| Gemini 2.0 Flash | $0.075 | $0.30 | Very cost-effective |
| Gemini 2.0 Pro | $1.25 | $5.00 | Good for complex tasks |

*Prices approximate and subject to change. Check vendor pricing pages for current rates.*

### Cost Optimization Strategies

#### 1. Model Routing

Route requests to the cheapest model that can handle them.

```python
def route_request(request):
    """Route to appropriate model based on task complexity."""
    if request.task_type == "simple_extraction":
        return "claude-haiku-4-5-20251001"  # Cheapest
    elif request.task_type == "clinical_summary":
        return "claude-sonnet-4-5-20250929"  # Best value
    elif request.task_type == "complex_diagnosis":
        return "claude-opus-4-5-20251101"  # Highest quality
```

#### 2. Prompt Caching

Reuse cached system prompts and few-shot examples. Reduces input token costs by up to 90% for repeated prefixes.

| Provider | Caching Feature | Savings |
|----------|----------------|---------|
| **Anthropic** | Prompt caching (beta) | Up to 90% on cached prefix |
| **Google** | Context caching | Reduced cost for repeated context |
| **OpenAI** | Automatic caching | Automatic for repeated prefixes |

#### 3. Semantic Caching

Cache responses by semantic similarity, not exact match.

```
User query: "What are the side effects of metformin?"
→ Check semantic cache (embedding similarity > 0.95)
→ Cache hit? Return cached response
→ Cache miss? Call LLM, cache response
```

#### 4. Token Budget Management

```python
# Set per-request and daily token budgets
TOKEN_BUDGETS = {
    "clinical_summary": {"max_input": 4000, "max_output": 2000},
    "medication_check": {"max_input": 1000, "max_output": 500},
    "daily_total": 5_000_000,  # 5M tokens/day
}
```

---

## 4. Reliability & Resilience

### Multi-Provider Fallback

```python
PROVIDER_CHAIN = [
    {"provider": "anthropic", "model": "claude-sonnet-4-5-20250929", "timeout": 30},
    {"provider": "google", "model": "gemini-2.0-flash", "timeout": 30},
    {"provider": "openai", "model": "gpt-4o", "timeout": 30},
]

async def reliable_llm_call(prompt, providers=PROVIDER_CHAIN):
    """Call LLM with automatic failover across providers."""
    for provider in providers:
        try:
            return await call_provider(provider, prompt)
        except (RateLimitError, TimeoutError, ServiceError) as e:
            log.warning(f"{provider['provider']} failed: {e}")
            continue
    raise AllProvidersFailedError("All LLM providers exhausted")
```

### LLM Gateway

Use an LLM gateway/proxy to centralize routing, caching, rate limiting, and fallback logic.

| Gateway | Type | Key Features |
|---------|------|-------------|
| **LiteLLM** | Open-source proxy | 100+ models, unified API, cost tracking |
| **Portkey** | Managed gateway | Caching, fallback, guardrails, analytics |
| **AI Gateway (Cloudflare)** | Edge proxy | Caching, rate limiting, logging |
| **Custom (NGINX + middleware)** | DIY | Full control |

### Rate Limit Management

```python
import asyncio
from collections import defaultdict

class RateLimiter:
    """Per-provider rate limiting with token bucket."""

    def __init__(self):
        self.limits = {
            "anthropic": {"rpm": 1000, "tpm": 100000},
            "openai": {"rpm": 500, "tpm": 80000},
            "google": {"rpm": 1500, "tpm": 200000},
        }

    async def acquire(self, provider, estimated_tokens):
        """Wait if rate limit would be exceeded."""
        # Token bucket implementation
        ...
```

---

## 5. LLM Testing Patterns

### Test Categories

| Test Type | What It Validates | Example |
|-----------|-------------------|---------|
| **Unit tests** | Individual prompt behavior | "Does this prompt extract medications correctly?" |
| **Regression tests** | No degradation on prompt changes | "Does v2.0 still handle edge cases from v1.0?" |
| **Safety tests** | Refusal of harmful requests | "Does it refuse to provide dosing for controlled substances?" |
| **Adversarial tests** | Prompt injection resistance | "Does it ignore injected instructions?" |
| **Performance tests** | Latency and throughput | "Is p95 latency under 2 seconds?" |
| **Cost tests** | Token usage within budget | "Is average cost per request under $0.05?" |

### Evaluation Framework

```python
# Example: LLM output evaluation pipeline
def evaluate_clinical_summary(output, reference):
    """Evaluate clinical summary quality."""
    scores = {
        "completeness": check_all_sections_present(output, ["S", "O", "A", "P"]),
        "accuracy": check_no_hallucinated_facts(output, reference),
        "icd10_correct": check_icd10_codes(output),
        "medication_extracted": check_medications_complete(output, reference),
        "safety_language": check_safety_disclaimers(output),
        "phi_free": check_no_phi_leakage(output),
    }
    return scores
```

### Continuous Evaluation

Run automated evaluations on a schedule against a held-out test set:

```
Daily:
  - Run 100 test cases through production prompts
  - Compare scores against baseline thresholds
  - Alert if any metric drops > 5%

Weekly:
  - Full evaluation suite (500+ cases)
  - Cost analysis and trend reporting
  - Model comparison (is a newer model better?)

Monthly:
  - Red team testing (adversarial inputs)
  - PHI leakage audit
  - Clinical accuracy review with domain experts
```

---

## 6. CI/CD for LLM Applications

### Pipeline Stages

```
1. Code/Prompt Change
   ↓
2. Lint & Validate (prompt schema, template syntax)
   ↓
3. Unit Tests (individual prompt evaluation)
   ↓
4. Integration Tests (RAG pipeline + LLM end-to-end)
   ↓
5. Safety Tests (adversarial inputs, PHI checks)
   ↓
6. Cost Estimation (projected token usage)
   ↓
7. Staging Deployment (shadow mode / canary)
   ↓
8. Production Deployment (gradual rollout)
```

### Prompt Deployment Strategies

| Strategy | Risk | Speed | Best For |
|----------|------|-------|----------|
| **Direct deploy** | High | Instant | Low-risk prompt tweaks |
| **Canary** | Low | Slow | Major prompt changes |
| **Shadow mode** | None | Slow | New models or major rewrites |
| **A/B test** | Low | Medium | Comparing approaches |

---

## 7. Healthcare-Specific LLMOps

### Compliance Requirements

| Requirement | Implementation |
|-------------|---------------|
| **Audit logging** | Log every LLM request/response (minus PHI) |
| **PHI monitoring** | Automated PHI detection in outputs |
| **Access control** | Role-based access to LLM endpoints |
| **Data residency** | Ensure data stays in compliant regions |
| **Model approval** | Clinical team must approve model/prompt changes |
| **Incident response** | Playbook for LLM-related clinical incidents |

### Clinical Validation Workflow

```
Prompt Change Proposed
  → Automated evaluation (accuracy, safety, cost)
  → Clinical informaticist review
  → Physician sign-off (for clinical-facing prompts)
  → Staged rollout with monitoring
  → Post-deployment clinical accuracy audit
```

---

## Quick Reference: LLMOps Checklist

### Before Production
- [ ] Prompts versioned in source control
- [ ] Evaluation suite with baseline metrics
- [ ] Safety tests (adversarial, PHI leakage)
- [ ] Cost projections and token budgets
- [ ] Multi-provider fallback configured
- [ ] Rate limiting in place
- [ ] Observability instrumented (traces, metrics)

### In Production
- [ ] Daily automated evaluations running
- [ ] Cost dashboards and alerts configured
- [ ] Latency monitoring with SLA alerts
- [ ] PHI leakage detection active
- [ ] Prompt change deployment pipeline operational
- [ ] Incident response playbook documented

### Ongoing
- [ ] Weekly cost reviews
- [ ] Monthly clinical accuracy audits
- [ ] Quarterly red team exercises
- [ ] Model upgrade evaluation pipeline
- [ ] Prompt optimization reviews

---

## Related Resources

- [Prompt Engineering Guide](./prompt-engineering-guide.md) — Prompt design techniques
- [MLOps Patterns](../patterns/ai-design/mlops/) — General ML operations patterns
- [Agent Patterns](../patterns/agents/) — Operating agent systems
- [Training Patterns](../patterns/ai-design/training/README.md) — When to fine-tune vs. prompt
- [Architecture Framework](./architecture-framework.md) — Well-Architected principles
- [Testing Guide](./testing-guide.md) — General testing patterns

## References

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Anthropic Production Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/production)
- [Google Vertex AI MLOps](https://cloud.google.com/vertex-ai/docs/start/introduction-mlops)

## Version History

- **v1.0** (2026-02-05): Initial version
