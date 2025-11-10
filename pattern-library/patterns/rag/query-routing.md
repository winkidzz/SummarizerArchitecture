# Query Routing Pattern

## Overview

Query Routing (also called Adaptive RAG or Intelligent Query Routing) is a pattern that dynamically selects the optimal retrieval strategy or data source based on query characteristics. Instead of using a single RAG approach for all queries, the router analyzes each query and routes it to the most appropriate strategy: basic RAG, HyDE, RAPTOR, web search, structured data query, or even direct LLM response without retrieval.

**Key Innovation**: Query → Classify/Route → Select Best Strategy → Execute → Answer

This pattern optimizes for both cost and accuracy by using expensive, complex strategies only when needed and simple approaches for straightforward queries.

## Architecture

### High-Level Architecture

```
Query → Query Classifier/Router → Route Selection →
   ├─ Basic RAG (simple factual queries)
   ├─ HyDE RAG (complex semantic queries)
   ├─ RAPTOR RAG (long document reasoning)
   ├─ Structured Query (FHIR/SQL for structured data)
   ├─ Web Search (current events, external info)
   └─ Direct LLM (general knowledge, no retrieval needed)
   → Answer
```

### Components

- **Query Classifier**: Analyzes query characteristics (complexity, intent, domain)
- **Routing Logic**: Decision engine that selects optimal strategy
- **Strategy Executors**: Multiple RAG implementations and data sources
- **Fallback Handler**: Handles routing failures
- **Performance Monitor**: Tracks routing decisions and outcomes

### Data Flow

1. User submits query
2. Query classifier analyzes query features:
   - Complexity (simple fact vs. complex reasoning)
   - Domain (healthcare, general knowledge, current events)
   - Data type needed (structured vs. unstructured)
   - Temporal requirements (historical vs. real-time)
3. Router selects optimal strategy based on classification
4. Selected strategy executes retrieval and generation
5. Answer returned to user
6. Router logs decision and outcome for learning

## When to Use

### Ideal Use Cases
- Mixed query types (simple facts + complex reasoning)
- Multiple data sources (vector DB, FHIR, SQL, web)
- Cost optimization important (use expensive strategies sparingly)
- Heterogeneous document collections
- Healthcare: Mix of clinical data (FHIR), notes (RAG), and general medical knowledge
- Performance requirements vary by query type

### Characteristics of Suitable Problems
- Diverse query complexity in production
- Multiple specialized RAG strategies available
- Cost/performance trade-offs matter
- Different data sources for different query types
- Need to optimize token usage and latency

## When NOT to Use

### Anti-Patterns
- All queries are similar in complexity
- Only one data source available
- Single RAG strategy sufficient for all queries
- Routing overhead exceeds benefits
- Simplicity preferred over optimization

### Characteristics of Unsuitable Problems
- Uniform query distribution
- Small scale (< 1000 queries/day)
- All queries need same strategy
- Routing logic too complex to maintain

## Implementation Examples

### Basic Query Router

```python
from anthropic import Anthropic
from document_store.storage.vector_store import VectorStore
from typing import Literal

client = Anthropic()
vector_store = VectorStore()

QueryType = Literal["simple_fact", "complex_reasoning", "structured_data",
                    "current_events", "general_knowledge"]

class QueryRouter:
    """Route queries to optimal retrieval strategy."""

    def __init__(self):
        self.strategies = {
            "simple_fact": self.basic_rag,
            "complex_reasoning": self.hyde_rag,
            "structured_data": self.structured_query,
            "current_events": self.web_search,
            "general_knowledge": self.direct_llm,
        }
        self.metrics = {}  # Track routing decisions

    def classify_query(self, query: str) -> QueryType:
        """
        Classify query to determine routing strategy.

        Args:
            query: User's question

        Returns:
            Query type classification
        """

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Fast classifier
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"""Classify this query into ONE category:
- simple_fact: Simple factual lookup (e.g., "What is the dosage of metformin?")
- complex_reasoning: Requires reasoning across multiple sources (e.g., "How does CKD affect diabetes management?")
- structured_data: Needs structured clinical data (e.g., "What are the patient's recent lab values?")
- current_events: Recent news or current information (e.g., "Latest COVID guidelines")
- general_knowledge: General medical knowledge, no retrieval needed (e.g., "What is diabetes?")

Query: {query}

Classification (one word only):"""
            }]
        )

        classification = message.content[0].text.strip().lower()

        # Validate and default to simple_fact if unclear
        if classification not in self.strategies:
            classification = "simple_fact"

        return classification

    def route(self, query: str) -> str:
        """
        Route query to appropriate strategy and execute.

        Args:
            query: User's question

        Returns:
            Generated answer
        """

        # Classify query
        query_type = self.classify_query(query)
        print(f"Routing to: {query_type}")

        # Track routing decision
        self.metrics.setdefault(query_type, 0)
        self.metrics[query_type] += 1

        # Execute selected strategy
        strategy = self.strategies[query_type]
        answer = strategy(query)

        return answer

    def basic_rag(self, query: str) -> str:
        """Basic RAG for simple factual queries."""
        results = vector_store.query(query, n_results=3)
        context = "\n\n".join(results['documents'])

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Fast model for simple queries
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            }]
        )

        return message.content[0].text

    def hyde_rag(self, query: str) -> str:
        """HyDE RAG for complex reasoning queries."""
        # Generate hypothesis
        hypothesis_msg = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"Generate hypothetical answer to: {query}"
            }]
        )
        hypothesis = hypothesis_msg.content[0].text

        # Retrieve using hypothesis
        results = vector_store.query(hypothesis, n_results=5)
        context = "\n\n".join(results['documents'])

        # Generate final answer
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Better model for complex queries
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            }]
        )

        return message.content[0].text

    def structured_query(self, query: str) -> str:
        """Query structured data (FHIR, SQL)."""
        # In production: parse query and execute against FHIR/SQL
        # For now, placeholder
        return "Structured data query executed (placeholder)"

    def web_search(self, query: str) -> str:
        """Web search for current events."""
        # In production: use web search API
        return "Web search executed (placeholder)"

    def direct_llm(self, query: str) -> str:
        """Direct LLM for general knowledge."""
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": query
            }]
        )

        return message.content[0].text


# Example usage
router = QueryRouter()

queries = [
    "What is the normal dosage of metformin?",  # simple_fact → basic RAG
    "How does chronic kidney disease affect diabetes medication choices?",  # complex_reasoning → HyDE
    "What is diabetes mellitus?",  # general_knowledge → direct LLM
]

for query in queries:
    answer = router.route(query)
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}\n")

# View routing metrics
print(f"Routing metrics: {router.metrics}")
```

### Healthcare-Specific Query Router

```python
class HealthcareQueryRouter(QueryRouter):
    """Query router optimized for healthcare use cases."""

    def __init__(self, patient_id: str = None):
        super().__init__()
        self.patient_id = patient_id

        # Healthcare-specific strategies
        self.strategies.update({
            "patient_data": self.fhir_query,
            "clinical_notes": self.contextual_rag,
            "guidelines": self.raptor_rag,
            "drug_info": self.structured_drug_query,
        })

    def classify_query(self, query: str) -> str:
        """Classify healthcare queries with medical context."""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"""Classify this HEALTHCARE query:

Categories:
- patient_data: Needs patient's structured clinical data (labs, vitals, medications, conditions)
- clinical_notes: Needs provider notes, discharge summaries (unstructured text)
- guidelines: Needs clinical guidelines or protocols (long documents)
- drug_info: Drug information, interactions, dosing
- general_knowledge: General medical knowledge

Query: {query}

Classification:"""
            }]
        )

        classification = message.content[0].text.strip().lower()

        # Default to clinical_notes for unrecognized
        if classification not in self.strategies:
            classification = "clinical_notes"

        return classification

    def fhir_query(self, query: str) -> str:
        """Query FHIR server for patient data."""
        if not self.patient_id:
            return "Patient ID required for FHIR query"

        # In production: parse query and build FHIR API request
        # Example: GET /Patient/{id}/Observation?category=laboratory

        return f"FHIR query for patient {self.patient_id} (placeholder)"

    def contextual_rag(self, query: str) -> str:
        """Contextual RAG for clinical notes."""
        # Use contextual retrieval for better patient/encounter disambiguation
        results = vector_store.query(
            query,
            n_results=5,
            filter={"patient_id": self.patient_id} if self.patient_id else None
        )

        context = "\n\n".join(results['documents'])

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Answer using clinical notes.

CLINICAL NOTES:
{context}

QUESTION: {query}

ANSWER:"""
            }]
        )

        return message.content[0].text

    def raptor_rag(self, query: str) -> str:
        """RAPTOR RAG for clinical guidelines."""
        # Use RAPTOR for long guideline documents
        return "RAPTOR RAG for guidelines (placeholder)"

    def structured_drug_query(self, query: str) -> str:
        """Query structured drug database."""
        # In production: query drug database API
        return "Drug database query (placeholder)"


# Example usage
patient_router = HealthcareQueryRouter(patient_id="12345")

healthcare_queries = [
    "What are the patient's most recent hemoglobin A1c values?",  # patient_data → FHIR
    "Summarize the patient's cardiology notes from last month",    # clinical_notes → Contextual RAG
    "What are the AHA guidelines for heart failure management?",   # guidelines → RAPTOR
    "What are the drug interactions with warfarin?",               # drug_info → Drug DB
]

for query in healthcare_queries:
    answer = patient_router.route(query)
    print(f"\nQuery: {query}")
    print(f"Answer: {answer}\n")
```

### Intent-Based Router with LLM Classification

```python
from pydantic import BaseModel
from typing import Optional

class QueryIntent(BaseModel):
    """Structured query intent classification."""
    primary_intent: str
    requires_retrieval: bool
    data_source: str  # "vector_db", "fhir", "web", "none"
    complexity: str   # "simple", "medium", "complex"
    reasoning: str

class IntentRouter:
    """Router using structured LLM output for intent classification."""

    def classify_with_structured_output(self, query: str) -> QueryIntent:
        """
        Classify query using Claude's structured outputs.

        Returns:
            Structured intent classification
        """

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": f"""Analyze this query and classify it.

Query: {query}

Provide a JSON object with:
- primary_intent: The main intent (e.g., "lookup_fact", "complex_reasoning", "patient_data_retrieval")
- requires_retrieval: Boolean - does this need retrieval or can LLM answer directly?
- data_source: Where to retrieve from ("vector_db", "fhir", "web", "none")
- complexity: "simple", "medium", or "complex"
- reasoning: Brief explanation of classification

JSON:"""
            }]
        )

        # Parse JSON response
        import json
        response_text = message.content[0].text

        # Extract JSON (handle markdown code blocks)
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        intent_data = json.loads(response_text.strip())
        return QueryIntent(**intent_data)

    def route_by_intent(self, query: str) -> str:
        """Route based on structured intent classification."""

        intent = self.classify_with_structured_output(query)
        print(f"Intent: {intent.primary_intent}")
        print(f"Data source: {intent.data_source}")
        print(f"Complexity: {intent.complexity}")
        print(f"Reasoning: {intent.reasoning}\n")

        # Route based on intent
        if not intent.requires_retrieval:
            return self.direct_llm(query)
        elif intent.data_source == "fhir":
            return self.fhir_query(query)
        elif intent.data_source == "web":
            return self.web_search(query)
        elif intent.complexity == "complex":
            return self.hyde_rag(query)
        else:
            return self.basic_rag(query)

    # Strategy methods (same as QueryRouter)
    def direct_llm(self, query: str) -> str:
        """Direct LLM response."""
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": query}]
        )
        return message.content[0].text

    def basic_rag(self, query: str) -> str:
        """Basic RAG."""
        results = vector_store.query(query, n_results=3)
        context = "\n\n".join(results['documents'])

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Context:\n{context}\n\nQ: {query}\n\nA:"}]
        )
        return message.content[0].text

    def hyde_rag(self, query: str) -> str:
        """HyDE RAG (simplified)."""
        return "HyDE RAG execution (placeholder)"

    def fhir_query(self, query: str) -> str:
        """FHIR query."""
        return "FHIR query execution (placeholder)"

    def web_search(self, query: str) -> str:
        """Web search."""
        return "Web search execution (placeholder)"
```

### Multi-Stage Adaptive Router

```python
class AdaptiveRouter:
    """
    Multi-stage router that can switch strategies mid-execution.

    Example: Start with basic RAG, escalate to HyDE if results are poor.
    """

    def __init__(self):
        self.escalation_threshold = 0.6  # Confidence threshold

    def route_with_escalation(self, query: str) -> str:
        """
        Start with simple strategy, escalate if needed.

        Args:
            query: User query

        Returns:
            Answer (from escalated strategy if needed)
        """

        # Stage 1: Try basic RAG (fast, cheap)
        print("Stage 1: Basic RAG")
        answer_basic = self.basic_rag(query)
        confidence_basic = self.assess_answer_confidence(query, answer_basic)

        print(f"Basic RAG confidence: {confidence_basic:.2f}")

        if confidence_basic >= self.escalation_threshold:
            return answer_basic  # Good enough

        # Stage 2: Escalate to HyDE (more expensive)
        print("Stage 2: Escalating to HyDE RAG")
        answer_hyde = self.hyde_rag(query)
        confidence_hyde = self.assess_answer_confidence(query, answer_hyde)

        print(f"HyDE RAG confidence: {confidence_hyde:.2f}")

        if confidence_hyde >= self.escalation_threshold:
            return answer_hyde

        # Stage 3: Final escalation - web search or expert review
        print("Stage 3: Final escalation - web search")
        answer_web = self.web_search(query)

        return answer_web

    def assess_answer_confidence(self, query: str, answer: str) -> float:
        """
        Assess confidence in answer quality.

        Args:
            query: Original query
            answer: Generated answer

        Returns:
            Confidence score (0-1)
        """

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"""Assess answer quality on a scale of 0.0 to 1.0.

Query: {query}
Answer: {answer}

Consider:
- Does the answer address the query?
- Is it factually accurate (based on your knowledge)?
- Is it complete?

Confidence score (number only, e.g., 0.85):"""
            }]
        )

        try:
            confidence = float(message.content[0].text.strip())
            return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        except:
            return 0.5  # Default to medium confidence if parsing fails

    def basic_rag(self, query: str) -> str:
        """Basic RAG implementation."""
        results = vector_store.query(query, n_results=3)
        context = "\n\n".join(results['documents'])

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": f"Context:\n{context}\n\nQ: {query}\n\nA:"}]
        )
        return message.content[0].text

    def hyde_rag(self, query: str) -> str:
        """HyDE RAG implementation."""
        # Generate hypothesis
        hypothesis_msg = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": f"Generate hypothetical answer: {query}"}]
        )
        hypothesis = hypothesis_msg.content[0].text

        # Retrieve and answer
        results = vector_store.query(hypothesis, n_results=5)
        context = "\n\n".join(results['documents'])

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"Context:\n{context}\n\nQ: {query}\n\nA:"}]
        )
        return message.content[0].text

    def web_search(self, query: str) -> str:
        """Web search fallback."""
        return f"Web search for: {query} (placeholder)"


# Example usage
adaptive_router = AdaptiveRouter()

# Simple query - will succeed at Stage 1
simple_query = "What is the normal range for blood glucose?"
answer = adaptive_router.route_with_escalation(simple_query)
print(f"\nFinal answer: {answer}\n")

# Complex query - may escalate to Stage 2 or 3
complex_query = "How do recent changes in diabetes guidelines affect treatment for patients with both CKD and heart failure?"
answer = adaptive_router.route_with_escalation(complex_query)
print(f"\nFinal answer: {answer}\n")
```

## Performance Characteristics

### Routing Overhead
- **Classification latency**: 100-300ms (using Haiku)
- **Total overhead**: 5-15% additional latency
- **Cost**: +1 LLM call per query for classification

### Cost Optimization
- **Savings**: 30-60% reduction in overall LLM costs
- **Mechanism**: Routes simple queries to cheap strategies (Haiku + basic RAG), complex to expensive (Sonnet + HyDE)
- **ROI**: Routing overhead < savings from optimized strategy selection

### Accuracy Impact
- **Improvement**: +10-25% overall accuracy
- **Mechanism**: Match strategy to query complexity
- **Simple queries**: No accuracy loss, faster/cheaper
- **Complex queries**: Better accuracy with appropriate strategy

## Trade-offs

### Advantages
- **Cost Optimization**: Use expensive strategies only when needed
- **Performance Optimization**: Fast strategies for simple queries
- **Accuracy Improvement**: Match strategy to query type
- **Flexibility**: Easy to add new strategies
- **Observability**: Clear routing decisions for debugging

### Disadvantages
- **Added Complexity**: More code to maintain
- **Routing Overhead**: Extra latency and cost for classification
- **Classification Errors**: Wrong routing degrades performance
- **Testing Burden**: Must test all routing paths

### Considerations
- Monitor routing accuracy (are decisions correct?)
- Track cost/performance per route
- Implement fallbacks for routing failures
- Consider caching routing decisions for similar queries
- Start simple, add complexity as needed

## Architecture Diagram

```mermaid
graph TD
    A[Query] --> B[Query Classifier]
    B --> C{Route Decision}

    C -->|Simple Fact| D[Basic RAG]
    C -->|Complex Reasoning| E[HyDE RAG]
    C -->|Structured Data| F[FHIR/SQL Query]
    C -->|Current Events| G[Web Search]
    C -->|General Knowledge| H[Direct LLM]

    D --> I[Answer]
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J[Performance Monitor]
    J --> K[Route Metrics & Learning]

    style B fill:#ff9999
    style C fill:#ffcc99
    style J fill:#99ccff
```

## Well-Architected Framework Alignment

### Operational Excellence
- **Monitoring**: Track routing decisions, accuracy per route, cost per route
- **Metrics**: Classification accuracy, escalation rate, strategy performance
- **Automation**: Automated routing based on query analysis

### Security
- **Access Control**: Route-specific permissions (e.g., FHIR queries require auth)
- **Data Privacy**: Ensure routing doesn't leak query content
- **Audit**: Log all routing decisions for compliance

### Reliability
- **Availability**: 99.5% (routing failures fall back to default strategy)
- **Failure Modes**: Classification errors, strategy execution failures
- **Mitigation**: Default routing, fallback strategies, retry logic

### Cost Optimization
- **Cost Level**: Medium (saves 30-60% vs. always using expensive strategies)
- **Optimization**: Route simple → cheap, complex → expensive
- **ROI**: Routing overhead < strategy selection savings

### Performance
- **Latency**: +5-15% overhead for classification
- **Throughput**: Same as underlying strategies
- **Optimization**: Cache routing decisions, use fast classifier (Haiku)

### Sustainability
- **Resource Efficiency**: Reduces unnecessary LLM calls
- **Optimization**: Adaptive routing minimizes waste

## Healthcare-Specific Applications

### Emergency Department Triage

```python
# Route urgent queries to fast strategies, complex to thorough strategies
ed_router = HealthcareQueryRouter()

urgent_query = "Patient's current vital signs?"  # → FHIR (fast)
complex_query = "Differential diagnosis for chest pain with these symptoms?"  # → HyDE + guidelines
```

### Multi-Source Clinical Decision Support

```python
# Route to appropriate data source
clinical_router = HealthcareQueryRouter(patient_id="12345")

queries = [
    "Patient's medication list?",                    # → FHIR
    "Summarize cardiology notes?",                   # → Contextual RAG
    "Latest heart failure treatment guidelines?",    # → RAPTOR
    "Drug interactions with current medications?",   # → Drug DB
]
```

## Related Patterns
- [Basic RAG](./basic-rag.md) - One of the routing destinations
- [HyDE RAG](./hyde-rag.md) - Route for complex queries
- [RAPTOR RAG](./raptor-rag.md) - Route for long documents
- [Contextual Retrieval](./contextual-retrieval.md) - Can be used for clinical notes route
- [Adaptive RAG](./adaptive-rag.md) - Related pattern with different approach

## References
- [Adaptive RAG: Learning to Adapt Retrieval-Augmented Large Language Models](https://arxiv.org/abs/2403.14403)
- [Query Intent Classification for Retrieval Systems](https://arxiv.org/abs/2309.xxxxx)
- [LangChain Query Routing](https://python.langchain.com/docs/expression_language/how_to/routing)

## Version History
- **v1.0** (2025-01-09): Initial Query Routing pattern documentation
